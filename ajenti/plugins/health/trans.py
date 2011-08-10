from ajenti.utils import str_fsize

def trans_None(x):
    return x

def trans_float(x):
    return '%.2f'%x['value']

def trans_fsize(x):
    return str_fsize(int(x['value']))

def trans_percent(x):
    if float(x['max']) == float(x['min']):
        return '0%'
    return '%.2f%%'%((float(x['value'])-float(x['min']))/(float(x['max'])-float(x['min']))*100)

def trans_fsize_percent(x):
    return '%s (%s)'%(trans_fsize(x), trans_percent(x))

def trans_yesno(x):
    return 'Yes' if x['value'] else 'No'

def trans_onoff(x):
    return 'On' if x['value'] else 'Off'

def trans_running(x):
    return 'Running' if x['value'] else 'Stopped'
