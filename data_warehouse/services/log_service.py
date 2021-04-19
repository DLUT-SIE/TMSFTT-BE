'''日志查询服务'''


class LogService:
    '''日志查询服务'''

    @staticmethod
    def get_tail_n_logs(n_tail):
        '''define how to get tail of logs.'''
        if n_tail <= 0:
            n_tail = 1
        filename = '/django-server.log'
        with open(filename, 'r') as log_file:
            lines = log_file.readlines()
        length = len(lines)
        if n_tail >= length:
            return lines
        return lines[-n_tail:]
