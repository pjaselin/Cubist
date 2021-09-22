cimport numpy as np
np.import_array()

# external declarations for cubist and predictions function from the top.c file
cdef extern from "src/top.c":
    void cubist(char **namesv, char **datav, int *unbiased,
                char **compositev, int *neighbors, int *committees,
                double *sample, int *seed, int *rules, double *extrapolation,
                char **modelv, char **outputv)
    void predictions(char **casev, char **namesv, char **datav, char **modelv, 
                     double *predv, char **outputv)

# define the Python functions that interface with the C functions
def _cubist(namesv_, datav_, unbiased_, compositev_, neighbors_, committees_, 
            sample_, seed_, rules_, extrapolation_, modelv_, outputv_):
    """
    Train and retun Cubist model and output from C code
    """
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
    cubist(&namesv, &datav, &unbiased, &compositev, &neighbors, &committees, 
           &sample, &seed, &rules, &extrapolation, &modelv, &outputv);
    return (modelv, outputv)


def _predictions(casev_, namesv_, datav_, modelv_, 
                 np.ndarray[double, ndim=1, mode="c"] predv_, outputv_):
    """
    Obtain predictions using existing Cubist model and return output if raised
    Reference: https://scipy-lectures.org/advanced/interfacing_with_c/interfacing_with_c.html#id13
    """
    cdef char *casev = casev_;
    cdef char *namesv = namesv_;
    cdef char *datav = datav_;
    cdef char *modelv = modelv_;
    cdef char *outputv = outputv_;
    predictions(&casev, &namesv, &datav, &modelv, 
                <double*> np.PyArray_DATA(predv_), &outputv);
    return (predv_, outputv)
