import os
import shutil
import subprocess
import glob

RESULTS_DIR = r"C:\tmp\topcoat-telemetry"
GRUNT_PATH = "C:/Users/labuser/AppData/Roaming/npm/node_modules/grunt-cli/bin/grunt"


def checkEnvVars():
    if not os.environ.get("DEVICE_NAME"):
        raise RuntimeError("Please set DEVICE_NAME env var (no spaces allowed yet)")

    if not os.environ.get("CHROMIUM_SRC"):
        raise RuntimeError("Please set CHROMIUM_SRC env var.")


def prepareResultsDir():
    print "runAll.py: Preparing results dir %s" % RESULTS_DIR
    if os.path.isdir(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
    os.makedirs(RESULTS_DIR)


def prepareTelemetryTests():
    print "runAll.py: Preparing telemetry tests"
    subprocess.call("node %s telemetry" % GRUNT_PATH)


def runTests():
    print "runAll.py: Running telemetry tests, results in %s" % RESULTS_DIR

    CHROMIUM_SRC = os.environ.get("CHROMIUM_SRC")

    topcoat_test_files = glob.glob(os.getcwd() + "/test/perf/telemetry/perf/page_sets/*.json")
    telemetry_tests = ["loading_benchmark", "smoothness_benchmark"]

    for f in topcoat_test_files:
        topcoat_test_file = f.split(os.sep)[-1]
        topcoat_test_name = topcoat_test_file.split(".")[0]
        print "runAll.py: Running tests for %s" % topcoat_test_name

        for telemetry_test in telemetry_tests:
            cmd = CHROMIUM_SRC + "/tools/perf/run_multipage_benchmarks "                  + \
                "--browser=system "                                                       + \
                telemetry_test + " "                                                      + \
                CHROMIUM_SRC + "/tools/perf/page_sets/%s " % topcoat_test_file            + \
                "-o " + RESULTS_DIR + "/%s_%s.txt" % (telemetry_test, topcoat_test_name)
            print cmd
            subprocess.call("python " + cmd)


def submitResults():
    print "runAll.py: Pushing telemetry data to the server"
    result_files = glob.glob(RESULTS_DIR + "/*.txt")
    print result_files
    for rf in result_files:
        cmd = "node %s telemetry-submit --path=%s --device=%s" % (GRUNT_PATH, rf, os.environ.get("DEVICE_NAME"))
        subprocess.call(cmd)


checkEnvVars()
prepareResultsDir()
prepareTelemetryTests()
runTests()
submitResults()