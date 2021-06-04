
cdef extern from "src/top.c":
    void cubist(char **namesv, char **datav, int *unbiased,
                char **compositev, int *neighbors, int *committees,
                double *sample, int *seed, int *rules, double *extrapolation,
                char **modelv, char **outputv)

cdef extern from "src/top.c":
    void predictions(char **casev, char **namesv, char **datav,
                     char **modelv, double *predv, char **outputv)