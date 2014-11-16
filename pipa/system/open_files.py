
import pipa
import gzip, bz2

import pipa


def open_files(filenames):
    for name in filenames:
        if name.endswith(".gz"):
            pipa.logger.debug("open %s" % name)
            file = gzip.open(name)
        elif name.endswith(".bz2"):
            pipa.logger.debug("open %s" % name)
            file = bz2.BZ2File(name)
        else:
            pipa.logger.debug("open %s" % name)
            file = open(name)
        yield file
        file.close()