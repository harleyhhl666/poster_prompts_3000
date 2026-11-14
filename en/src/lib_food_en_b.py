import glob, os, importlib.util
ARCHETYPES = []
for _f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'parts', 'lib_food_en_b', 'p*.py'))):
    _s = importlib.util.spec_from_file_location(os.path.basename(_f)[:-3], _f); _m = importlib.util.module_from_spec(_s); _s.loader.exec_module(_m)
    ARCHETYPES += _m.ITEMS
