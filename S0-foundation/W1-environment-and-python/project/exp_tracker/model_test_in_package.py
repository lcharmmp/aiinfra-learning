from models import Experiment
if __name__ == '__main__':

    ex1 = Experiment('model_test_in_package')

import sys
for s in sys.path:
    print(s)