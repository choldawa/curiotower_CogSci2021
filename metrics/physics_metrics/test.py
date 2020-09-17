import numpy as np

from metrics.feature_extractor import FeatureExtractor
from metrics.readout_model import IdentityModel
from metrics.metric_model import BatchMetricModel

from physics_metrics.linear_readout_model import LinearRegressionReadoutModel, \
        LogisticRegressionReadoutModel
from physics_metrics.flex.metric_fns import particle_position_mse, object_position_mse, \
        accuracy

from physics.data.data_provider import SequenceNewDataProvider \
        as DataProvider
from physics.models.constructor.fromrecords import ParticleGraphConstructorFromRecords \
        as GraphConstructor
from physics.models.dynamics.hrn import HRNDynamicsModel \
        as GraphDynamics
from physics.models.loss import HierarchicalLoss \
        as GraphLoss
from physics.run.train_step import rollout_model


DATA_PARAMS = {
        'data': ['/Users/damian/data/collide2_test/new_tfdata'],
        'enqueue_batch_size': 64,
        'sequence_len': 42,
        'buffer_size': 16,
        'batch_size': 16,
        'shift_selector': slice(1, 2, None),
        'test': True,
        'main_source_key': 'full_particles',
        'sources': ['full_particles', 'graph', 'materials', 'static_mesh', 'object_data',
            'is_colliding_dynamic'],
        'delta_time': 1,
        'filter_rule': (lambda data, is_moving: data[is_moving[0]], ['is_moving']),
        'shuffle': True,
        'seed': 0,
        'use_legacy_sequence_mode': 1,
        'subsources': ['graph'],
        }

MODEL_PARAMS = {
        'data_sequence_len': DATA_PARAMS['sequence_len'],
        'model_sequence_len': 2,
        }



def build_data(data_params):
    data_provider = DataProvider(**data_params)
    dataset = data_provider.build_datasets(data_params['batch_size'])
    data = iter(dataset)
    return data


def build_model(model_params, model_fn):
    graph_constructor = GraphConstructor()
    dynamics_model = GraphDynamics()
    loss = GraphLoss()

    def particle_model_fn(data):
        results = rollout_model(graph_constructor, dynamics_model, loss,
            data, model_params['data_sequence_len'], model_params['model_sequence_len'])
        predictions = np.stack([res['full_particles'][:, -1] \
                for res in results], axis = 1)
        return predictions

    def object_model_fn(data):
        results = rollout_model(graph_constructor, dynamics_model, loss,
                data, model_params['data_sequence_len'], model_params['model_sequence_len'])
        predictions = np.stack([res['full_particles'][:, -1] \
                for res in results], axis = 1)
        # Predictions and labels dimensions must be the same except for the last dimension
        # TODO Fix this simple hack because model outputs particles not objects
        obj_ids = list(np.unique(predictions[..., 14]))
        if 0.0 in obj_ids:
            obj_ids.remove(0.0)
        obj_ids = np.array(obj_ids)
        # HACK: Split particles evenly across objects
        splits = [predictions.shape[-2] // len(obj_ids)] * (len(obj_ids) - 1)
        predictions = np.split(predictions, splits, axis = -2)
        predictions = [np.mean(pred, axis=-2) for pred in predictions]
        predictions = np.stack(predictions, axis=-2)
        return predictions

    def scene_model_fn(data):
        predictions = object_model_fn(data)
        # TODO FIX HACK: Average over time and particle dimension to generate scene description
        predictions = np.mean(predictions, axis=(1,2))
        return predictions

    if model_fn == 'particle_model_fn':
        return particle_model_fn
    elif model_fn == 'object_model_fn':
        return object_model_fn
    elif model_fn == 'scene_model_fn':
        return scene_model_fn
    else:
        raise NotImplementedError('Unknown model function!')


def particle_label_fn(data):
    labels = data['full_particles'][:, MODEL_PARAMS['model_sequence_len'] - 1:]
    return labels


def object_label_fn(data):
    labels = data['object_data'][:, MODEL_PARAMS['model_sequence_len'] - 1:]
    return labels


def collision_label_fn(data):
    labels = data['is_colliding_dynamic'][:, MODEL_PARAMS['model_sequence_len'] - 1:]
    labels = np.any(labels, axis=(1,2)).astype(np.int32)
    return labels


def main():
    # Example 1: Classification of "collision occured" via logistic regression

    # Build physics model
    feature_model = build_model(MODEL_PARAMS, "scene_model_fn")
    feature_extractor = FeatureExtractor(feature_model)

    # Construct data providers
    train_data = build_data(DATA_PARAMS)
    test_data = build_data(DATA_PARAMS)

    # Build logistic regression model
    readout_model = LogisticRegressionReadoutModel()

    # Score unfitted predictions
    metric_model = BatchMetricModel(feature_extractor, readout_model,
            accuracy, collision_label_fn,
            )
    metric_model.fit(train_data)
    result = metric_model.score(test_data)

    print("Collision categorization accuracy:", result)

    # Example 2: Direct position prediction without fitting via IdentityModel

    # Build physics model
    feature_model = build_model(MODEL_PARAMS, "object_model_fn")
    feature_extractor = FeatureExtractor(feature_model)

    # Construct data providers
    train_data = build_data(DATA_PARAMS)
    test_data = build_data(DATA_PARAMS)

    # Build regression model (no regression)
    readout_model = IdentityModel()

    # Score unfitted predictions
    metric_model = BatchMetricModel(feature_extractor, readout_model,
            #particle_position_mse, particle_label_fn
            object_position_mse, object_label_fn,
            )
    result = metric_model.score(test_data)

    print("Position MSE without fitting:", result)

    # Example 3: Position prediction via linear regression

    # Build physics model
    feature_model = build_model(MODEL_PARAMS, "object_model_fn")
    feature_extractor = FeatureExtractor(feature_model)

    # Construct data providers
    train_data = build_data(DATA_PARAMS)
    test_data = build_data(DATA_PARAMS)

    # Build regression model (linear)
    readout_model = LinearRegressionReadoutModel()

    # Fit and score linear regression predictions
    metric_model = BatchMetricModel(feature_extractor, readout_model,
            #particle_position_mse, particle_label_fn
            object_position_mse, object_label_fn,
            )
    metric_model.fit(train_data)
    result = metric_model.score(test_data)
    print("Position MSE with linear fitting:", result)


if __name__ == '__main__':
    main()
