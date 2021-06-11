
cdef extern from "src/top.c":
    void cubist(char **namesv, char **datav, int *unbiased,
                char **compositev, int *neighbors, int *committees,
                double *sample, int *seed, int *rules, double *extrapolation,
                char **modelv, char **outputv)

cdef extern from "src/top.c":
    void predictions(char **casev, char **namesv, char **datav,
                     char **modelv, double *predv, char **outputv)

def py_cubist(namesv: str, datav: str, unbiased, compositev: str, neighbors, committees, sample, seed, rules, extrapolation, modelv: str, outputv: str):
    cubist(namesv, datav, unbiased, compositev, neighbors, committees, sample, seed, rules, extrapolation, modelv, outputv)

def py_predictions(casev:str, namesv:str, datav:str, modelv: str, predv, outputv: str):
    predictions(casev, namesv, datav, modelv, predv, outputv)