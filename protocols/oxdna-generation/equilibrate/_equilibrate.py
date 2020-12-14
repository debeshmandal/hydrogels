from softnanotools.logger import Logger
logger = Logger('EQUILIBRATE')

def main(fname):
    return

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    main(**vars(parser.parse_args()))
    