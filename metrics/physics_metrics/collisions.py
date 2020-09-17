from metrics.feature_extractor import FeatureExtractor
from metrics.readout_model import IdentityModel
from metrics.metric_model import BatchMetricModel

from physics_metrics.linear_readout_model import LinearRegressionReadoutModel, \
        LogisticRegressionReadoutModel
from physics_metrics.flex.metric_fns import particle_position_mse, object_position_mse, \
        accuracy

metric_model = MetricModel(
    feature_extractor=FeatureExtractor(lambda data: np.reshape(data, [len(data), -1])),
    readout_model=sklearn.linear_model.LogisticRegression(),
    metric_fn=(lambda preds, labels: sklearn.metrics.accuracy_score(labels, preds))
)

def binary_collision_metric_agg_func(res):
    '''
    An aggregation function to use with Tfutils and FLEX data
    '''
    out = {}
    for k,v in res.items():
        res[k] = np.concatenate(v, axis=0)
    N = int(len(res['is_colliding_dynamic']) * 0.8)
    train_labels = np.any(np.abs(res['is_colliding_dynamic'][:N,4:,0]), axis=1)
    metric_model.fit(res['nodes_level_1_pred'][:N], train_labels)
    train_accuracy = metric_model.score(res['nodes_level_1_pred'][:N], train_labels)
    test_labels = np.any(np.abs(res['is_colliding_dynamic'][N:,4:,0]), axis=1)
    test_accuracy = metric_model.score(res['nodes_level_1_pred'][N:], test_labels)
    out['collision_train_accuracy'] = train_accuracy
    out['collision_test_accuracy'] = test_accuracy

    # compute with gt inputs
    metric_model.fit(res['nodes_level_1'][:N,4:], train_labels)
    gttrain_accuracy = metric_model.score(res['nodes_level_1'][:N,4:], train_labels)
    gttest_accuracy = metric_model.score(res['nodes_level_1'][N:,4:], test_labels)
    out['collision_gttrain_accuracy'] = gttrain_accuracy
    out['collision_gttest_accuracy'] = gttest_accuracy
    out['collision_baseline_accuracy'] = sklearn.metrics.accuracy_score(np.ones_like(test_labels), test_labels)

    return out
