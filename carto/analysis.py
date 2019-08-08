from datetime import datetime
import time
import re
import os
import json
from .color import colored, Color
import base64

AFW_API_URL = 'api/{api_version}/analysis'

HEADERS = {
    'content-type': 'application/json',
    'accept': 'application/json'
}


class AnalysisClient(object):
    def __init__(self, auth_client, api_version='v4'):
        self.auth_client = auth_client
        self.api_url = AFW_API_URL.format(api_version=api_version)

        self.api_key = getattr(self.auth_client, 'api_key', None)
        self.username = getattr(self.auth_client, 'username', None)
        self.base_url = self.auth_client.base_url

    def _url(self, *parts):
        return '/'.join((self.api_url,) + parts)

    def list_jobs(self):
        res = self.auth_client.send(self._url('jobs'), 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def create_job(self, job_definition):
        url = self._url('jobs')
        res = self.auth_client.send(url, 'POST', json=job_definition, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def read_job(self, job_id):
        url = self._url('jobs', job_id)
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_job(
        self, job_id, job_params, schedule=None, on_changed_table=None
    ):
        url = self._url('jobs', job_id, 'schedule')
        params = {}
        if schedule:
            params['schedule'] = schedule
        if on_changed_table:
            params['on_changed_table'] = on_changed_table
        res = self.auth_client.send(url, 'POST', params=params, json=job_params, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def list_schedules(self, job_id):
        url = self._url('jobs', job_id, 'schedules')
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_status(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id)
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def schedule_executions(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id, 'executions')
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def execution_log(
        self, job_id, schedule_id, execution_id, type='stdout', offset=None
    ):
        url = self._url(
            'jobs', job_id,
            'schedule', schedule_id,
            'execution', execution_id,
            'log'
        )
        res = self.auth_client.send(url, 'GET', params={'type': type, 'offset': offset}, headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def execution_logs(self, job_id, schedule_id, execution_id):
        url = self._url(
            'jobs', job_id,
            'schedule', schedule_id,
            'execution', execution_id,
            'debug'
        )
        res = self.auth_client.send(url, 'GET', headers=HEADERS)
        logs = self.auth_client.get_response_data(res, False)
        if logs is not None:
            logs = logs.decode()
        return logs

    def remove_job(self, job_id):
        url = self._url('jobs', job_id)
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def stop_schedule(self, job_id, schedule_id):
        url = self._url('jobs', job_id, 'schedule', schedule_id)
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)

    def stop_schedules(self, job_id):
        url = self._url('jobs', job_id, 'schedules')
        res = self.auth_client.send(url, 'DELETE', headers=HEADERS)
        return self.auth_client.get_response_data(res, True)


TASK_GROUP = 'analysis'  # we have always one task group named analysis


class DefaultOutput:

    @staticmethod
    def print(*args):
        print(*args)

    @staticmethod
    def clear():
        os.system('clear')


def _color_logs(logs):
    if logs and Color.enabled:
        logs = re.sub(r'^EVENTS$', Color.COLORS['blue'], logs, flags=re.MULTILINE)
        logs = re.sub(r'^STDOUT$', Color.END + Color.COLORS['yellow'], logs, flags=re.MULTILINE)
        logs = re.sub(r'^STDERR$', Color.END + Color.COLORS['red'], logs, flags=re.MULTILINE)
        logs = logs + Color.END
    return logs


def _status_color(status):
    if status == 'purged':
        color = ['blink', 'gray']
    elif status == 'pending':
        color = 'pink'
    elif status == 'dead':
        color = 'orange'
    elif status == 'running':
        color = ['bold', 'blue']
    else:
        color = []
    return color


class SessionIds:

    def __init__(self, file=None):
        self._tokens = {}
        self._counters = {}
        self._ids_from_tokens = {}
        self._file = file
        self._load()

    def _load(self):
        if self._file and os.path.isfile(self._file):
            with open(self._file, "r") as input:
                data = json.load(input)
            self._tokens = data['tokens']
            self._counters = data['counters']
            self._ids_from_tokens = data['ids']

    def _save(self):
        if self._file:
            data = {
                'tokens': self._tokens,
                'counters': self._counters,
                'ids': self._ids_from_tokens
            }
            with open(self._file, "w") as output:
                output.write(json.dumps(data))

    def job_token(self, job):
        return self._session_token(job.name(), [job.job_id])

    def schedule_token(self, job_id, schedule_id):
        job_token = self._tokens.get(job_id)
        return self._session_token(job_token + '/', [job_id, schedule_id])

    def execution_token(self, job_id, schedule_id, execution_id):
        schedule_token = self._tokens.get(schedule_id)
        # assert
        # [job_id, schedule_id] == self.__ids_from_tokens(schedule_token)
        return self._session_token(
            schedule_token + '/', [job_id, schedule_id, execution_id]
        )

    def _session_token(self, prefix, ids):
        id = ids[-1]
        found_id = self._tokens.get(id)
        if found_id:
            return found_id
        count = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = count
        if len(ids) == 1:
            # job identifier
            if count > 1:
                token = '_'.join([prefix, str(count)])
            else:
                token = prefix
        else:
            token = prefix + str(count)
        self._tokens[id] = token
        self._ids_from_tokens[token] = ids
        self._save()
        return token

    def ids(self, token):
        return self._ids_from_tokens.get(token)


class AnalysisContext:
    """Analysis objects hold a context used to access the AAPI.

       They contain both the AAPI interface and parameters that define
       how to use it when updating the state of AAPI objects.

        Attributes:
            aapi (AApi): AApi REST client interface
            minimum_update_time (float): Minimum time in seconds to wait before
                                         updating the state of an object
            autosleep: When requesting an early update sleep till the minimum
            time (rather than skipping the update)
    """

    def __init__(
        self,
        auth_client,
        api_version='v4',
        minimum_update_time=1,
        autosleep=True,
        persist_tokens=None,
        output=DefaultOutput
    ):
        """
        Args:
            api_config: dictionary with AAPI configuration
            (url_base, user, api_key)
            minimum_update_time
            autosleep
        """
        self.api = AnalysisClient(auth_client, api_version)
        self.minimum_update_time = minimum_update_time
        self.autosleep = autosleep
        self.tokens = SessionIds(persist_tokens)
        self.output = output

    def create_job(self, job_definition):
        result = self.api.create_job(job_definition)
        return self.job(result['job_id'])

    def jobs(self):
        return [self.job(j['job_id']) for j in self.api.list_jobs()]

    def job(self, job_id):
        return Job(self, job_id)

    def job_by_name(self, name):
        return next(job for job in self.jobs() if job.name() == name)

    def job_by_token(self, token):
        return self.job(*self.tokens.ids(token))

    def schedule_by_token(self, schedule_token):
        return Schedule(
            self, *self.tokens.ids(schedule_token)
        )

    def execution_by_token(self, execution_token):
        # workaround: executions only reachable through
        # schedules ATM
        job_id, schedule_id, execution_id = self.tokens.ids(execution_token)
        schedule = Schedule(self, job_id, schedule_id)
        return schedule.execution(execution_id)


class Updatable:
    """Base class for updatable AAPI Objects
    """

    def __init__(self, context):
        self._context = context
        self.update_time = None

    def _time_since_update(self):
        return time.time() - (self.update_time or 0)

    def _updated_now(self):
        self.update_time = time.time()

    def _need_to_update(self):
        t = self._time_since_update()
        wait = self.update_time and t < self._context.minimum_update_time
        if wait:
            if self._context.autosleep:
                time.sleep(self._context.minimum_update_time - t)
            else:
                return False
        return True


class Job(Updatable):
    def __init__(self, context, job_id):
        super().__init__(context)
        self.job_id = job_id
        self.definition = None
        self.schedule_ids = None
        self.update()

    def update(self):
        if self._need_to_update():
            self.definition = self._context.api.read_job(self.job_id)
            self.token = self._context.tokens.job_token(self)
            self.schedule_ids = [
                s['schedule_id']
                for s in self._context.api.list_schedules(self.job_id)
            ]

    def name(self):
        return self.definition['name']

    def version(self):
        return self.definition['version']

    def user(self):
        return self.definition['user']

    def image(self):
        return self.definition['image']

    def schedule(self, schedule_id):
        return Schedule(self._context, self.job_id, schedule_id)

    def schedule_by_token(self, schedule_token):
        return Schedule(
            self._context, *self._context.ids(schedule_token)
        )

    def schedules(self):
        return [self.schedule(id) for id in self.schedule_ids]

    def info(self, details=False):
        info = '{token} {version} ({user})'.format(
            token=colored('bold', self.token),
            version=self.version(),
            user=self.user()
        )
        if (details):
            info += ' ' + self.details()
        return info

    def details(self):
        return 'image: {image}'.format(image=self.image())

    def execute(self, params, schedule=None, table=None):
        schedule = self._context.api.schedule_job(
            self.job_id,
            job_params=params,
            schedule=schedule,
            on_changed_table=table
        )
        schedule_id = schedule['schedule_id']
        return self.schedule(schedule_id)

    def execute_and_follow(self, params, schedule=None, table=None):
        schedule = self.execute(params, schedule, table)
        schedule.follow()
        return schedule

    def execute_and_get_output(self, params, schedule=None, table=None, verbose=False, decodeJson=False):
        schedule = self.execute(params, schedule, table)
        if not (schedule.is_periodic() or schedule.is_triggered()):
            exec = schedule.follow(not verbose)
            return exec and exec.output(decodeJson)
        return schedule

    def remove(self):
        return self._context.api.remove_job(self.job_id)

    def stop_schedules(self):
        return self._context.api.stop_schedules(self.job_id)

    def __str__(self):
        return '{} {}'.format(super().__repr__(), self.name())

    __repr__ = __str__


class Schedule(Updatable):
    """
        Attributes:
            status
            children:
              ['Pending'] ['Dead'] ['Running']
            summary:
              ['Complete'] ['Starting'] ['Failed']
              ['Lost'] ['Queued'] ['Running']
            executions
    """

    def __init__(self, context, job_id, schedule_id):
        super().__init__(context)
        self.job_id = job_id
        self.schedule_id = schedule_id
        self._raw_status = None
        self._set_raw_status(self._raw_status)
        self._executions = None
        self.update()

    def _set_raw_status(self, status):
        self._raw_status = status or {}
        self.status = self._raw_status.get('status')
        if (self.status and self.status != 'purged'):
            self.time = _timefromtimestamp(self._raw_status.get('time', 0))
            self.schedule = self._raw_status.get('schedule')
            s = self._raw_status.get('summary', {})
            self.children = s.get('Children')
            self.summary = s.get('Summary', {}).get(TASK_GROUP)
        else:
            self.time = None
            self.schedule = None
            self.children = None
            self.summary = None
        self.definition = self._raw_status.get('definition', {})
        self.type = self.definition.get('type')
        self.table = self.definition.get('table')
        self.scheduling_time = self.definition.get('scheduling_time')
        if not self.time and self.scheduling_time:
            self.time = _timefromiso(self.scheduling_time)

    def _fetch_executions(self):
        if self._executions_pending:
            self._executions_pending = False
            execs = self._context.api.schedule_executions(
                self.job_id, self.schedule_id
            )
            # TODO: is this necessary?
            # (does Nomad API guarantee the result order? )
            execs.sort(key=lambda e: e['time'])
            self._executions = [
                Execution(
                    self._context, self.job_id, self.schedule_id, exec
                )
                for exec in execs
            ]

    def update(self):
        if self._need_to_update():
                self.token = self._context.tokens.schedule_token(
                    self.job_id, self.schedule_id
                )
                new_raw_status = self._context.api.schedule_status(
                    self.job_id, self.schedule_id
                )
                if new_raw_status != self._raw_status:  # FIXME: ok??
                    self._set_raw_status(new_raw_status)
                    self._executions_pending = True
                    self._updated_now()
                    return True
                self._updated_now()
        return False

    def is_periodic(self):
        return self.schedule is not None

    def is_triggered(self):
        return self.type == 'trigger'

    def info(self):
        # TODO: identify schedule by user, time of creation
        # option to include job name
        # note: user will only be available when adding db metadata to api
        # time could be obtained from "SubmitTime":1548327600000512493
        return self._info_prefix() + self._info_suffix()

    def _info_prefix(self):
        return '{id} {t}'.format(
            id=colored('bold', self.token),
            t=_timetoiso(self.time)
        )

    def _info_suffix(self):
        if self.is_periodic():
            return ' ({s})'.format(s=colored('pink', self.schedule))
        elif self.is_triggered():
            return ' (on changed {t})'.format(t=colored('pink', self.table))
        else:
            return ''

    def show(self, details=False):
        color = _status_color(self.status)
        self._context.output.print(
            self._info_prefix()
            + ' : ' + colored(color, self.status)
            + ' : ' + self.summary_info()
            + self._info_suffix()
        )
        if details:
            self._context.output.print(self.details())

    def details(self):
        return ''

    def summary_info(self):
        if self.summary is None:
            return ''
        if self.type == 'now':
            return 'C:{c} S:{s} F:{f} L:{l} Q:{q} R:{r}'.format(
                c=colored('green', self.summary['Complete']),
                s=colored('blue', self.summary['Starting']),
                f=colored('red', self.summary['Failed']),
                l=colored('orange', self.summary['Lost']),  # noqa: E741
                q=colored('pink', self.summary['Queued']),
                r=colored('yellow', self.summary['Running'])
            )
        else:
            # For 'periodic', 'trigger', the summary is empty;
            # it would be interesting to show the summary of the
            # dispatch children jobs as part of the corresponding
            # execution status.
            return 'P:{p} R: {r} D:{d}'.format(
                p=colored(_status_color('pending'), self.children['Pending']),
                r=colored(_status_color('running'), self.children['Running']),
                d=colored(_status_color('dead'), self.children['Dead'])
            )

    def follow(self, silent=False):
        # TODO: if self.is_periodic() filter execs for most recent cron point
        last_exec = None
        while self.status != 'dead':
            self.update()
            if not silent:
                self._context.output.clear()
                self.show()
            last_exec_running = False
            for exec in self.executions():
                last_exec = exec
                last_exec_running = exec.running()
                if not silent:
                    exec.show(with_logs=last_exec_running)
            if last_exec and not last_exec_running and not silent:
                self._context.output.print(last_exec.logs())
        return last_exec

    def executions(self):
        self._fetch_executions()
        return self._executions

    # def execution(self, execution_id):
    #     return Execution(
    #         self._context,
    #         self.job_id,
    #         self.schedule_id,
    #         execution_id
    #     )

    def execution_by_token(self, execution_token):
        return self.execution(self._context.tokens.ids(execution_token)[-1])

    def execution(self, execution_id):
        return next(
            exe
            for exe in self.executions()
            if exe.execution_id == execution_id
        )

    def stop(self):
        return self._context.api.stop_schedule(self.job_id, self.schedule_id)

    def last_outputs(self, n=1, only_finished=True, only_succesful=False, decodeJson=False, filter=None):
        self.update()

        def select(exec):
            selected = True
            selected = not only_finished or exec.finished()
            selected = selected and (not only_succesful or exec.successful)
            selected = selected and (not filter or filter(exec))
            return selected

        execs = self.executions()
        if execs and len(execs) > 0:
            execs = [exec for exec in execs if select(exec)]
            execs.sort(key=lambda e: e.finish_time(), reverse=True)
            if len(execs) > 0:
                return list(map(lambda exec: exec.output(decodeJson), execs))
        return []


def _timefromiso(txt):
    if not txt:
        return None
    txt = re.sub(r'.(\d\d\d)\d+', r'.\1', txt).replace("Z", "+00:00")
    return datetime.fromisoformat(txt)


def _timetoiso(t):
    if t is None:
        return ''
    return t.isoformat(sep=' ', timespec='seconds')


def _timefromtimestamp(value):
    return datetime.utcfromtimestamp(value/1000000000.0)


EVENT_TIME = re.compile(r'\bTime:(\d+)\b')


class Execution:

    def __init__(self, context, job_id, schedule_id, exec):
        self._context = context
        self.job_id = job_id
        self.schedule_id = schedule_id
        self.execution_id = exec['execution_id']
        self._raw_data = exec
        # dummy_state = exec['state']  # None
        # Time of execution creation
        self._create_t = _timefromtimestamp(exec['time'])
        e = exec['execution']
        self._state = e['state']  # pending -> running -> dead
        self._failed = None
        self._start_t = None
        self._finish_t = None
        if (self._state != 'pending'):
            self._failed = e['failed']
            self._start_t = e['started_at'] and _timefromiso(e['started_at'])
            if (self._state == 'dead'):
                self._finish_t = (
                    e['finished_at'] and _timefromiso(e['finished_at'])
                )
        self.token = self._context.tokens.execution_token(
            self.job_id, self.schedule_id, self.execution_id
        )

    def pending(self):
        return self._state == 'pending' or self._state is None

    def running(self):
        return self._state == 'running'

    def finished(self):
        return self._state == 'dead'

    def success(self):
        return self.finished() and not self._failed

    def failed(self):
        return self.finished() and self._failed

    def allocation_time(self):
        return self._create_t

    def start_time(self):
        return self._start_t

    def finish_time(self):
        return self._finish_t

    def info(self, indent=''):
        msg = (
            indent
            + colored('bold', self.token)
            + ' '
            + _timetoiso(self.allocation_time())
            + ' : '
        )
        if self.pending():
            msg += colored('blue', 'pending')
        elif self.running():
            msg += (
                colored('yellow', 'running')
                + ' since {t}'.format(t=_timetoiso(self.start_time()))
            )
        elif self.success():
            msg += (
                colored('green', 'success')
                + ' (ran from {t1} to {t2})'.format(
                    t1=_timetoiso(self.start_time()),
                    t2=_timetoiso(self.finish_time())
                )
            )
        elif self.failed():
            msg += colored('red', 'error') + ' (ran from {t1} to {t2}'.format(
                t1=_timetoiso(self.start_time()),
                t2=_timetoiso(self.finish_time())
            )
        else:
            msg = str(self._raw_data) or '???'
        return msg

    def logs(self):
        logs = self._context.api.execution_logs(
            self.job_id,
            self.schedule_id,
            self.execution_id
        )

        def repltime(match):
            return _timetoiso(_timefromtimestamp(int(match.group(1))))

        if logs:
            print('>>>>>>>> LOGS')
            print(logs)
            print('----------------------------')
            print(repltime)
            logs = re.sub(EVENT_TIME, repltime, logs)
        return _color_logs(logs)

    def output(self, decodeJson=False):
        log = self._context.api.execution_log(
            self.job_id,
            self.schedule_id,
            self.execution_id,
            type='stdout'
        )
        result = None
        if log:
            result = base64.b64decode(log.get('Data', ''))
            if decodeJson:
                result = json.loads(result.decode())
        return result

    def show(self, with_logs=True):
        self._context.output.print(self.info())
        if with_logs:
            self._context.output.print(self.logs())
