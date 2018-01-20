import numpy as np
from sklearn.decomposition import PCA as SKLearnPCA
from sklearn.utils import check_array
from sklearn.utils.validation import check_is_fitted

from ..base import BaseDetector
from ..utils import timeit, OneDimArray, TwoDimArray

__all__ = ['PCA']


class PCA(BaseDetector):
    """Outlier detector using Principal Component Analysis (PCA).

    Parameters
    ----------
    fpr : float, default 0.01
        False positive rate. Used to compute the threshold.

    verbose : bool, default False
        Enable verbose output.

    kwargs : dict
        Other keywords passed to sklearn.decomposition.PCA().

    Attributes
    ----------
    components_ : array-like of shape (n_components, n_features)
        Principal axes in feature space, representing the directions of maximum
        variance in the data.

    explained_variance_ : array-like of shape (n_components,)
        Amount of variance explained by each of the selected components.

    explained_variance_ratio_ : array-like of shape (n_components,)
        Percentage of variance explained by each of the selected components.

    mean_ : array-like of shape (n_features,)
        Per-feature empirical mean, estimated from the training set.

    noise_variance_ : float
        Estimated noise covariance following the Probabilistic PCA model from
        Tipping and Bishop 1999.

    n_components_ : int
        Estimated number of components.

    singular_values_ : array-like of shape (n_components,)
        Singular values corresponding to each of the selected components.

    threshold_ : float
        Threshold.

    X_ : array-like of shape (n_samples, n_features)
        Training data.
    """

    @property
    def components_(self) -> TwoDimArray:
        return self._pca.components_

    @property
    def explained_variance_(self) -> OneDimArray:
        return self._pca.explained_variance_

    @property
    def explained_variance_ratio_(self) -> OneDimArray:
        return self._pca.explained_variance_ratio_

    @property
    def mean_(self) -> OneDimArray:
        return self._pca.mean_

    @property
    def noise_variance_(self) -> float:
        return self._pca.noise_variance_

    @property
    def n_components_(self) -> int:
        return self._pca.n_components_

    @property
    def singular_values_(self) -> OneDimArray:
        return self._pca.singular_values_

    def __init__(
        self,
        fpr:     float = 0.01,
        verbose: bool  = False,
        **kwargs
    ) -> None:
        super().__init__(fpr=fpr, verbose=verbose)

        self._pca = SKLearnPCA(**kwargs)

        self.check_params()

    def check_params(self) -> None:
        """Check validity of parameters and raise ValueError if not valid."""

        super().check_params()

    @timeit
    def fit(self, X: TwoDimArray, y: OneDimArray = None) -> 'PCA':
        """Fit the model according to the given training data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.

        y : ignored

        Returns
        -------
        self : PCA
            Return self.
        """

        self._pca.fit(X)

        self.X_         = check_array(X)
        anomaly_score   = self.anomaly_score()
        self.threshold_ = np.percentile(anomaly_score, 100. * (1. - self.fpr))

        return self

    def reconstruct(self, X: TwoDimArray) -> OneDimArray:
        """Apply dimensionality reduction to the given data, and transform the
        data back to its original space.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data.

        Returns
        -------
        X_rec : array-like of shape (n_samples, n_features)
        """

        return self._pca.inverse_transform(self._pca.transform(X))

    def anomaly_score(self, X: TwoDimArray = None) -> OneDimArray:
        """Compute the anomaly score for each sample.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features), default None
            Data.

        Returns
        -------
        anomaly_score : array-like of shape (n_samples,)
            Anomaly score for each sample.
        """

        return np.sqrt(np.sum(self.feature_wise_anomaly_score(X), axis=1))

    def feature_wise_anomaly_score(self, X: TwoDimArray = None) -> TwoDimArray:
        """Compute the feature-wise anomaly score for each sample.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features), default None
            Data.

        Returns
        -------
        anomaly_score : array-like of shape (n_samples, n_features)
            Feature-wise anomaly score for each sample.
        """

        check_is_fitted(self, 'X_')

        if X is None:
            X = self.X_

        return (X - self.reconstruct(X)) ** 2

    def score(self, X: TwoDimArray, y: OneDimArray = None) -> float:
        """Compute the mean log-likelihood of the given data.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Data.

        y : ignored

        Returns
        -------
        score : float
            Mean log-likelihood of the given data.
        """

        return self._pca.score(X)
