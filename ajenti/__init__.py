import subprocess

def version():
    release = '0.5-4'
    p = subprocess.Popen('git describe 2> /dev/null', 
            shell=True,
            stdout=subprocess.PIPE)
    if p.wait() != 0:
        return release
    return p.stdout.read()

# Generation declares which plugin version range to use
generation = '0'
