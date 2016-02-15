import os
import cPickle
import bz2
import tempfile


def normpath(*path):
    return os.path.normpath(os.path.abspath(os.path.expanduser(os.path.join(*path))))


def buildpath(filepath, directory):
    filepath = os.path.expanduser(filepath)
    if directory != '' and not os.path.isabs(filepath):
        filepath = os.path.join(directory, filepath)
    return normpath(filepath)


def create_directories(filepaths):
    dirset = set()
    for filepath in filepaths:
        path = os.path.dirname(filepath)
        path = normpath(path)
        dirset.add(path)
    for path in dirset:
        if not os.path.exists(path):
            os.makedirs(path)


def load_file(filename, directory='', typename='data', verbose=True):
    """Compressed version of the file is searched first."""
    filepath = buildpath(filename, directory)
    try:
        with open(filepath + '.bz2', 'rb') as fp:
            data_bz2 = bz2.decompress(fp.read())
            data = cPickle.loads(data_bz2)
    except EOFError:
        os.remove(filepath + '.bz2')
        raise EOFError('the file seemed corrupt and was deleted.')
    except IOError:
        with open(filepath, 'rb') as f:
            data = cPickle.load(f)

    return data


def save_file(data, filename, directory='', typename='data', verbose=True, compressed=True):
    filepath = buildpath(filename, directory)
    temp = tempfile.NamedTemporaryFile(delete=False)

    if compressed:
        temp.write(bz2.compress(cPickle.dumps(data, cPickle.HIGHEST_PROTOCOL), 9))
        filepath += '.bz2'
    else:
        temp.write(cPickle.dump(data, f, cPickle.HIGHEST_PROTOCOL))

    os.rename(temp.name, filepath)


def save_text(text, filename, directory='', typename='text', verbose=True):
    filepath = buildpath(filename, directory)
    with open(filepath, 'w') as f:
        f.write(text)
