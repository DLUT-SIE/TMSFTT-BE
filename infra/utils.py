'''Provide useful utilities shared among modules.'''


def format_file_size(size_in_bytes):
    '''Format human-readable file size.'''
    if size_in_bytes < 0 or size_in_bytes >= 1024**6:
        raise ValueError('参数超出转换范围')
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    val = size_in_bytes
    unit_idx = 0
    while val / 1024 > 1:
        unit_idx += 1
        val /= 1024
    return '{:.2f} {}'.format(val, units[unit_idx])
