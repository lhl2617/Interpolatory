from .Estimators.BasicAlgos.linear.calc import calc as basic_linear
from .Estimators.BasicAlgos.frame_repetition.calc import calc as basic_frame_rep
from .Estimators.BasicAlgos.oversampling.calc import calc as basic_oversampling

from .Estimators.MEMCI.unidir.fs.calc import calc as MEMCI_unidir_fs
from .Estimators.MEMCI.unidir.tss.calc import calc as MEMCI_unidir_tss
from .Estimators.MEMCI.unidir.hbma.calc import calc as MEMCI_unidir_hbma

from .Estimators.MEMCI.bidir.fs.calc import calc as MEMCI_bidir_fs
from .Estimators.MEMCI.bidir.tss.calc import calc as MEMCI_bidir_tss
from .Estimators.MEMCI.bidir.hbma.calc import calc as MEMCI_bidir_hbma

from .Estimators.MEMCI.bidir2.fs.calc import calc as MEMCI_bidir2_fs
from .Estimators.MEMCI.bidir2.tss.calc import calc as MEMCI_bidir2_tss
from .Estimators.MEMCI.bidir2.hbma.calc import calc as MEMCI_bidir2_hbma


EstimatorDictionary = {
    "basic_linear": basic_linear,
    "basic_frame_rep": basic_frame_rep,
    "basic_oversampling": basic_oversampling,
    
    "MEMCI_unidir_fs": MEMCI_unidir_fs,
    "MEMCI_unidir_tss": MEMCI_unidir_tss,
    "MEMCI_unidir_hbma": MEMCI_unidir_hbma,

    "MEMCI_bidir_fs": MEMCI_bidir_fs,
    "MEMCI_bidir_tss": MEMCI_bidir_tss,
    "MEMCI_bidir_hbma": MEMCI_bidir_hbma,
    
    "MEMCI_bidir2_fs": MEMCI_bidir2_fs,
    "MEMCI_bidir2_tss": MEMCI_bidir2_tss,
    "MEMCI_bidir2_hbma": MEMCI_bidir2_hbma
}

default_fs_options = {
    'b': {
        'description': 'size of single axis of block in pixels',
        'type': 'number',
        'value': 8
    },
    'r': {
        'description': 'number of rows of pixels in frame',
        'type': 'number',
        'value': 1080
    },
    'c': {
        'description': 'number of columns of pixels in frame',
        'type': 'number',
        'value': 1920
    },
    'w': {
        'description': 'size of single axis of search window in pixels',
        'type': 'number',
        'value': 22
    }
}

default_tss_options = {
    'b': {
        'description': 'size of single axis of block in pixels',
        'type': 'number',
        'value': 8
    },
    'r': {
        'description': 'number of rows of pixels in frame',
        'type': 'number',
        'value': 1080
    },
    'c': {
        'description': 'number of columns of pixels in frame',
        'type': 'number',
        'value': 1920
    },
    'steps': {
        'description': 'number of steps taken when searching',
        'type': 'number',
        'value': 3
    }
}

default_hbma_options = {
    'b_max': {
        'description': 'max size of single axis of block in pixels',
        'type': 'number',
        'value': 8
    },
    'b_min': {
        'description': 'min size of single axis of block in pixels',
        'type': 'number',
        'value': 4
    },
    'r': {
        'description': 'number of rows of pixels in frame',
        'type': 'number',
        'value': 1080
    },
    'c': {
        'description': 'number of columns of pixels in frame',
        'type': 'number',
        'value': 1920
    },
    'w': {
        'description': 'size of single axis of search window in pixels',
        'type': 'number',
        'value': 22
    },
    's': {
        'description': 'number of times the frames are downscaled',
        'type': 'number',
        'value': 2
    }
}

default_basic_options = {
    'r': {
        'description': 'number of rows of pixels in frame',
        'type': 'number',
        'value': 1080
    },
    'c': {
        'description': 'number of columns of pixels in frame',
        'type': 'number',
        'value': 1920
    }
}

EstimatorDocs = {
    "basic_linear": {
        'name': 'basic_linear',
        'description': 'Basic linear interpolation',
        'options': default_basic_options
    },
    "basic_frame_rep": {
        'name': 'basic_frame_rep',
        'description': 'Basic frame repetition interpolation',
        'options': default_basic_options
    },
    "basic_oversampling": {
        'name': 'basic_oversampling',
        'description': 'Basic oversampling interpolation',
        'options': default_basic_options
    },

    "MEMCI_unidir_fs": {
        'name': 'MEMCI_unidir_fs',
        'description': 'MEMCI, Unidirectional, Full Search',
        'options': default_fs_options
    },
    "MEMCI_unidir_tss": {
        'name': 'MEMCI_unidir_tss',
        'description': 'MEMCI, Unidirectional, Three Step Search',
        'options': default_tss_options
    },
    "MEMCI_unidir_hbma": {
        'name': 'MEMCI_unidir_hbma',
        'description': 'MEMCI, Unidirectional, Hierarchical Block Matching Algorithm',
        'options': default_hbma_options
    },

    "MEMCI_bidir_fs": {
        'name': 'MEMCI_bidir_fs',
        'description': 'MEMCI, Bidirectional, Full Search',
        'options': default_fs_options
    },
    "MEMCI_bidir_tss": {
        'name': 'MEMCI_bidir_tss',
        'description': 'MEMCI, Bidirectional, Three Step Search',
        'options': default_tss_options
    },
    "MEMCI_bidir_hbma": {
        'name': 'MEMCI_bidir_hbma',
        'description': 'MEMCI, Bidirectional, Hierarchical Block Matching Algorithm',
        'options': default_hbma_options
    },

    "MEMCI_bidir2_fs": {
        'name': 'MEMCI_bidir2_fs',
        'description': 'MEMCI, Bidirectional 2, Full Search',
        'options': default_fs_options
    },
    "MEMCI_bidir2_tss": {
        'name': 'MEMCI_bidir2_tss',
        'description': 'MEMCI, Bidirectional 2, Three Step Search',
        'options': default_tss_options
    },
    "MEMCI_bidir2_hbma": {
        'name': 'MEMCI_bidir2_hbma',
        'description': 'MEMCI, Bidirectional 2, Hierarchical Block Matching Algorithm',
        'options': default_hbma_options
    }
}

def getEDocs():
    print('# Interpolator Estimation Documentation')

    def getOptions(iDocOptions):
        for key, optionObj in iDocOptions.items():
            print(f'- `{key}`')
            desc = optionObj['description']
            print(f'    - {desc}')
            defaultVal = optionObj['value']
            print(f'    - Default: `{defaultVal}`')
            if optionObj['type'] == 'enum':
                print(f'    - Possible values: ')
                for i in range(len(optionObj['enum'])):
                    enumChoice = optionObj['enum'][i]
                    enumDesc = optionObj['enumDescriptions'][i]
                    print(f'        * `{enumChoice}`: {enumDesc}')

    for key, eDocObj in EstimatorDocs.items():
        print(f'## {key}')
        name = eDocObj['name']
        desc = eDocObj['description']
        print(f'- Name: `{name}``')
        print(f'- Description: `{desc}``')
        if 'options' in eDocObj:
            print(f'### Options')
            getOptions(eDocObj['options'])

        print('')
