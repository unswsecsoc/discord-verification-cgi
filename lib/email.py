import subprocess

def send_email(to, subject, body, cc=None):
  args = ['/usr/bin/mail', to, '-s', subject]
  if cc:
    if isinstance(cc, list):
      for i in cc:
        args.extend(['-c', cc])
    else:
      args.extend(['-c', cc])
  proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=None)
  proc.communicate(body.encode('ascii'))
  return proc.wait()
