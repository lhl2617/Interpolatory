import sys
import json
import os
import pathlib

sys.path.append('./src')
from src import util, Globals

mode_flag = None

if (len(sys.argv) > 1):
    args = sys.argv[1:]
    mode_flag = args[0]

    # if the last flag is -gui
    # turn off debugs
    last_arg = args[len(args) - 1]
    if (last_arg == '-gui'):
        # turn off debugs
        for flag in Globals.debug_flags:
            Globals.debug_flags[flag] = False
        args = args[:-1]


    # if the current last arg is `-pf=<progress-file-path>`
    # this is to signal progress of the conversion by writing into a file 
    last_arg = args[len(args) - 1]
    if (last_arg[:4] == '-pf='):
        file_path = last_arg[4:]
        util.progress_file_path = file_path
        args = args[:-1]

# limited_interpolators = list(LimitedInterpolatorDictionary.keys())
version = 'Interpolatory Simulator 1.0.1'

if mode_flag == '-h':
    import markdown
    basedir = pathlib.Path(__file__).parent.absolute()
    manual = open(f'{basedir}/docs/USAGEGUIDE.md', "r") 
    print(manual.read())
    manual.close() 

elif mode_flag == '-doc':
    from src.Interpolator import getIDocs
    getIDocs()
    
elif mode_flag == '-doc-estimator':
    from src.Estimator import getEDocs
    getEDocs()

# this schema is for gui
elif mode_flag == '-schema':
    from src.Interpolator import InterpolatorDocs
    print(json.dumps(InterpolatorDocs))

    
elif mode_flag == '-schema-estimator':
    from src.Estimator import EstimatorDocs
    print(json.dumps(EstimatorDocs))



elif mode_flag == '-mv' and len(args) == 2:
    import imageio
    from io import BytesIO
    video_path = args[1]
    video_file = open(video_path, 'rb')
    content = video_file.read()
    video = imageio.get_reader(BytesIO(content), 'ffmpeg', loop=True)
    print(json.dumps(video.get_meta_data()))

elif mode_flag == '-mi' and len(args) == 2:
    import imageio
    im_path = args[1]
    
    im = imageio.imread(im_path)
    print(im.shape)


    # print('')
    # print('- python3 main.py -i <input-video-path> -m <interpolation-mode>[:<settings>] -f <output-frame-rate> -o <output-file-path>')
elif mode_flag == '-i' and len(args) == 8 and '-m' == args[2] and '-f' == args[4] and '-o' == args[6]:
    import math
    from src.Interpolator import InterpolatorDictionary, checkValidMode
    input_video_path = args[1]
    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[3])

    checkValidMode(interpolation_mode, mode_flag)

    target_fps = int(args[5])
    output_video_path = args[7]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(target_fps, input_video_path, output_video_path, math.inf, **settings)
    interpolator.interpolate_video()



elif mode_flag == '-b' and len(args) >= 2:
    from src.Benchmark import benchmark
    from src.Interpolator import InterpolatorDictionary, checkValidMode
    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[1])

    checkValidMode(interpolation_mode, mode_flag)

    output_path = None
    if (len(args) > 2):
        output_path = args[2]

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(2, **settings)
    # print(settings)
    benchmark(interpolator, output_path)
    

elif mode_flag == '-t' and len(args) >= 7 and '-f' == args[2] and '-o' == args[5] :
    from src.Benchmark import benchmark, get_middle_frame
    from src.Interpolator import InterpolatorDictionary, checkValidMode
    interpolation_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[1])

    checkValidMode(interpolation_mode, mode_flag)

    frame_1_path = args[3]
    frame_2_path = args[4]
    output_file_path = args[6]
    ground_truth_path = None
    
    if (len(args) > 7):
        ground_truth_path = args[7]        

    interpolator_obj = InterpolatorDictionary[interpolation_mode]
    interpolator = interpolator_obj(2, **settings)
    get_middle_frame(interpolator, frame_1_path, frame_2_path, output_file_path, ground_truth_path)

elif mode_flag == '-e' and len(args) == 2:
    from src.Benchmark import benchmark, get_middle_frame
    from src.Estimator import EstimatorDictionary
    estimator_mode, settings = util.deconstruct_interpolation_mode_and_settings(args[1])

    estimator = EstimatorDictionary[estimator_mode]

    res = estimator(**settings)

    print(json.dumps(res))


elif mode_flag == '-ver':
    print(json.dumps(version))

    
    # print('')
    # print('- python3 main.py -dep')
    # print('Check whether normal requirements are met')
elif mode_flag == '-dep':
    import pkg_resources
    import pathlib
    import os
    
    basedir = pathlib.Path(__file__).parent.absolute()

    f = open(f'{basedir}{os.path.sep}requirements.txt', 'r')
    
    dependencies = f.read().split('\n')

    pkg_resources.require(dependencies)
    print('Success')

    # print('')
    # print('- python3 main.py -depcuda')
    # print('Check whether CUDA dependencies are met')
elif mode_flag == '-depcuda':
    import pkg_resources
    import pathlib
    import os
    
    basedir = pathlib.Path(__file__).parent.absolute()

    f = open(f'{basedir}{os.path.sep}cuda-requirements.txt', 'r')

    dependencies = f.read().split('\n')

    pkg_resources.require(dependencies)
    print('Success')

else:
    print(f'Unknown command. Run `python3 main.py -h` for a usage guide')


exit(0)