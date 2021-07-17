cimport numpy as np
np.import_array()

cdef extern from "src/top.c":
    void cubist(char **namesv, char **datav, int *unbiased,
                char **compositev, int *neighbors, int *committees,
                double *sample, int *seed, int *rules, double *extrapolation,
                char **modelv, char **outputv)
    void predictions(char **casev, char **namesv, char **datav,
                     char **modelv, double *predv, char **outputv)

def _cubist(namesv_, datav_, unbiased_, compositev_, neighbors_, committees_, sample_, seed_, rules_, extrapolation_, modelv_, outputv_):
    cdef char *namesv = namesv_;
    cdef char *datav = datav_;
    cdef int unbiased = unbiased_;
    cdef char *compositev = compositev_;
    cdef int neighbors = neighbors_;
    cdef int committees = committees_;
    cdef double sample = sample_;
    cdef int seed = seed_;
    cdef int rules = rules_;
    cdef double extrapolation = extrapolation_;
    cdef char *modelv = modelv_;
    cdef char *outputv = outputv_;
    cubist(&namesv, &datav, &unbiased, &compositev, &neighbors, &committees, &sample, &seed, &rules, &extrapolation, &modelv, &outputv);
    return (modelv, outputv)


def _predictions(casev_, namesv_, datav_, modelv_, np.ndarray[double, ndim=1, mode="c"] predv_, outputv_):
    cdef char *casev = casev_;
    cdef char *namesv = namesv_;
    cdef char *datav = datav_;
    cdef char *modelv = modelv_;
    # cdef double predv = predv_;
    cdef char *outputv = outputv_;
    # cdef double[:] testslice = np.zeros(predv_);
    predictions(&casev, &namesv, &datav, &modelv, <double*> np.PyArray_DATA(predv_), &outputv);
    return (predv_, outputv)