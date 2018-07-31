USE autoreduction;
# ======================================= #
# reduction_viewer_instrument

INSERT INTO reduction_viewer_instrument
    (id, name, is_active, is_paused)
VALUES
    (1, 'MUSR', 1, 0),
    (2, 'WISH', 1, 0),
    (3, 'GEM', 0, 0);

# ======================================= #
# reduction_viewer_status
INSERT INTO reduction_viewer_status
    (id, value)
VALUES
    (1, 'Error'),
    (2, 'Queued'),
    (3, 'Processing'),
    (4, 'Completed'),
    (5, 'Skipped');

# ======================================= #
# reduction_viewer_experiment
INSERT INTO reduction_viewer_experiment
    (id, reference_number)
VALUES
    (1, 123),
    (2, 456),
    (3, 789);

# ======================================= #
# reduction_viewer_reductionrun
INSERT INTO reduction_viewer_reductionrun
    (id, run_number, run_version, run_name, script, created, last_updated, started, finished, started_by, graph, message, reduction_log, admin_log, retry_when, cancel, hidden_in_failviewer, overwrite, experiment_id, instrument_id, retry_run_id, status_id)
VALUES
    #id - run no - run ver - run name -           script           -        created       -      last updated    -       started        -       finished      - started by -graph - message - reduction log  -  admin log - retry when - cancel - hidden - overwrite - exp id - inst id - retry id, status id 
    (1,    001,       0,    'test-run', 'print("running test run")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (2,    001,       0,    'test-run', 'print("running test run")', '2018-10-04 09:02:00', '2018-10-04 09:02:00', '2018-10-04 09:02:00', '2018-10-04 09:03:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    2   ,    2    ,     2   ,     4),
    (3,    001,       0,    'test-run', 'print("running test run")', '2018-10-04 09:04:00', '2018-10-04 09:04:00', '2018-10-04 09:04:00', '2018-10-04 09:05:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    3   ,    3    ,     3   ,     4),

    (4,    002,       0,    'test-run', 'print("running test run #2")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (5,    003,       0,    'test-run', 'print("running test run #3")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (6,    004,       0,    'test-run', 'print("running test run #4")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (7,    005,       0,    'test-run', 'print("running test run #5")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (8,    006,       0,    'test-run', 'print("running test run #6")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (9,    007,       0,    'test-run', 'print("running test run #7")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (10,   008,       0,    'test-run', 'print("running test run #8")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (11,   009,       0,    'test-run', 'print("running test run #9")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',   NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4),
    (12,   010,       0,    'test-run', 'print("running test run #10")', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:00:00', '2018-10-04 09:01:00',  NULL    , NULL, 'message', 'reduction-log', 'admin-log',    NULL    ,    0   ,    0   ,     0     ,    1   ,    1    ,     1   ,     4);
    

# ======================================= #
# reduction_viewer_datalocation
INSERT INTO reduction_viewer_datalocation
    (id, file_path, reduction_run_id)
VALUES
    (1, 'test/file/path/1.raw', 1),
    (2, 'test/file/path/WISH001.raw', 2),
    (3, 'test/file/path/GEM001.raw', 3),

    (4,  'test/file/path/2.raw',  4),
    (5,  'test/file/path/3.raw',  5),
    (6,  'test/file/path/4.raw',  6),
    (7,  'test/file/path/5.raw',  7),
    (8,  'test/file/path/6.raw',  8),
    (9,  'test/file/path/7.raw',  9),
    (10, 'test/file/path/8.raw',  10),
    (11, 'test/file/path/9.raw',  11),
    (12, 'test/file/path/10.raw', 12);

# ======================================= #
# reduction_viewer_reductionlocation
INSERT INTO reduction_viewer_reductionlocation
    (id, file_path, reduction_run_id)
VALUES
    (1, 'path/to/reduced/data/1', 1),
    (2, 'path/to/reduced/data/2', 2),
    (3, 'path/to/reduced/data/3', 3),

    (4,  'path/to/reduced/data/4',  4),
    (5,  'path/to/reduced/data/5',  5),
    (6,  'path/to/reduced/data/6',  6),
    (7,  'path/to/reduced/data/7',  7),
    (8,  'path/to/reduced/data/8',  8),
    (9,  'path/to/reduced/data/9',  9),
    (10, 'path/to/reduced/data/10',  10),
    (11, 'path/to/reduced/data/11',  11),
    (12, 'path/to/reduced/data/12', 12);

# ======================================= #
# reduction_viewer_notification
INSERT INTO reduction_viewer_notification
    (id, message, is_active, severity, is_staff_only)
VALUES
    (1, 'message', 0, 1, 0),
    (2, 'message', 0, 1, 0),
    (3, 'message', 0, 1, 0);

# ======================================= #
# reduction_viewer_setting
INSERT INTO reduction_viewer_setting
    (id, name, value)
VALUES
    (1, 'name', 'value'),
    (2, 'name', 'value'),
    (3, 'name', 'value');
