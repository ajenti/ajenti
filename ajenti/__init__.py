import subprocess

def version():
    release = '0.5.0'
    p = subprocess.Popen('git describe', 
            shell=True,
            stdout=subprocess.PIPE)
    if p.wait() != 0:
        return release
    return p.stdout.read()

# Generation declares which plugin version range to use
generation = 'dev'
