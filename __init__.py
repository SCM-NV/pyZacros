import scm.plams
from typing import Dict

from .__version__ import __version__

def __autoimport(path, folders):
    import os
    from os.path import join as opj
    is_module = lambda x: x.endswith('.py') and not x.startswith('__init__')

    ret = []
    for folder in folders:
        for dirpath, dirnames, filenames in os.walk(opj(path,folder)):
            modules = [os.path.splitext(f)[0] for f in filter(is_module, filenames)]
            relpath = os.path.relpath(dirpath, path).split(os.sep)
            for module in modules:
                imp = '.'.join(relpath + [module])
                tmp = __import__(imp, globals=globals(), fromlist=['*'], level=1)
                if hasattr(tmp, '__all__'):
                    ret += tmp.__all__
                    for name in tmp.__all__:
                        globals()[name] = vars(tmp)[name]
    return ret


__all__ = __autoimport(__path__[0], ['core','utils'])


def init(path=None, folder=None, config_settings:Dict=None):
    """Initializes pyZacros and PLAMS environment. It internally calls the scm.plams.init() method."""
    scm.plams.init( path=path, folder=folder, config_settings=config_settings )


def finish(otherJM=None):
    """Wait for all threads to finish and clean the environment. It internally calls the scm.plams.finish() method."""
    scm.plams.finish( otherJM=otherJM )


def load(filename):
    """Load previously saved job from ``.dill`` file. It internally calls the scm.plams.load() method."""
    scm.plams.load( filename )


def load_all(path, jobmanager=None):
    """Load all jobs from *path*. It internally calls the scm.plams.load_all() method."""
    scm.plams.load_all( path=path, jobmanager=jobmanager )


def delete_job(job):
    """Remove *job* from its corresponding |JobManager| and delete the job folder from the disk. Mark *job* as 'deleted'. It internally calls the scm.plams.delete_job() method."""
    scm.plams.load_all( job=job )


def log(message, level=0):
    """Log *message* with verbosity *level*. It internally calls the scm.plams.log() method."""
    scm.plams.load_all( message=message, level=level )
