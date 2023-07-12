import os
import json
import subprocess


def count_coverage(path, port):
    class_files = []
    jacoco_command2 = ''
    subdirs = [x[0] for x in os.walk(path)]
    for subdir in subdirs:
        if '/target/classes/' in subdir:
            target_dir = subdir[:subdir.rfind('/target/classes/') + 15]
            if target_dir not in class_files:
                class_files.append(target_dir)
                jacoco_command2 = jacoco_command2 + ' --classfiles ' + target_dir
        if '/build/classes/' in subdir:
            target_dir = subdir[:subdir.rfind('/build/classes/') + 14]
            if target_dir not in class_files:
                class_files.append(target_dir)
                jacoco_command2 = jacoco_command2 + ' --classfiles ' + target_dir

    jacoco_command2 = jacoco_command2 + ' --csv '
    jacoco_command1 = 'java -jar org.jacoco.cli-0.8.7-nodeps.jar report '
    jacoco_file = str(i) + '/' + port + '.csv'
    subprocess.run(jacoco_command1 + str(i) + "/jacoco" + port + ".exec" + jacoco_command2 + jacoco_file, shell=True)


def count_requests(file_name, service_name):
    request_total = 0
    request_2xx = 0
    path_2xx = {}
    time_2xx = 0
    req_2xx = 0
    request_4xx = 0
    request_500 = 0
    msg_500 = {}
    executed_operation = 0


    with open("specs/openapi/" + service_name + ".json", "r") as _f:
        spec = json.load(_f)


    # Iterate through the API specification and extract the paths
    for m in spec["paths"]:
        endpoint = m
        if len(endpoint) > 1 and endpoint[-1] == '/':
            endpoint = endpoint[:-1]
        if "{" in endpoint:
            temp = endpoint[:endpoint.find("{")]
            if temp not in msg_500:
                msg_500[temp] = []
                path_2xx[temp] = {}
        elif endpoint not in msg_500:
            msg_500[endpoint] = []
            path_2xx[endpoint] = {}

    with open(file_name, "r") as _f:
        lines = _f.readlines()

    current_path = ""
    operation = ""
    time_start = 0
    for k in range(len(lines)):
        if lines[k].strip() == "========REQUEST========":
            request_total = request_total + 1
            operation = lines[k+1].strip()
            current_path = lines[k+2].strip()
            if "?" in current_path:
                current_path = current_path[:current_path.find("?")]
        elif lines[k].strip() == "========RESPONSE========":
            status = int(lines[k+2].strip())

            if time_start == 0:
                time_start = float(lines[k+1].strip())
            if 200 <= status < 300:
                request_2xx = request_2xx + 1
                for path in path_2xx:
                    if path[-1] != '/' and path + "/" in path_2xx and path + "/" in current_path:
                        if operation not in path_2xx[path + "/"]:
                            path_2xx[path + "/"][operation] = float(lines[k+1].strip()) - time_start
                            req_2xx = request_total - 1
                    elif path in current_path:
                        if operation not in path_2xx[path]:
                            path_2xx[path][operation] = float(lines[k+1].strip()) - time_start
                            req_2xx = request_total - 1
            elif 400 <= status < 500:
                request_4xx = request_4xx + 1
            elif status == 500:
                # Let's store the message and check manually -- run new first and figure out supported keywords
                msg = lines[k + 3].strip()
                if "expected a valid value (" in msg:
                    msg = "expected a valid value ("
                elif "was expecting (JSON" in msg:
                    msg = "was expecting (JSON"
                elif "maybe a (non-standard)" in msg:
                    msg = "maybe a (non-standard)"
                elif "Expected space separating root-level values" in msg:
                    msg = "Expected space separating root-level values"
                elif "Unexpected close marker" in msg:
                    msg = "Unexpected close marker"
                elif "Unexpected end-of-input" in msg:
                    msg = "Unexpected end-of-input"
                elif "numeric value: expected digit (0-9)" in msg:
                    msg = "numeric value: expected digit (0-9)"
                elif "numeric value: Leading zeroes not" in msg:
                    msg = "numeric value: Leading zeroes not"
                else:
                    if "not found:" in msg:
                        msg = msg[:msg.find("not found:")]
                    if "meta" in msg:
                        msg = msg[:msg.find("meta")]
                    if "timestamp" in msg:
                        msg = msg[msg.find("status"):]
                    if "For input string" in msg:
                        msg = msg[:msg.find("For input string")]
                    if "path" in msg:
                        msg = msg[:msg.find("path")]
                    if "500," in msg:
                        msg = msg[msg.find("500,"):]
                    if "only regular" in msg:
                        msg = msg[msg.find("only regular"):]
                        msg = msg[:msg.find("at")]
                    if "numeric value:" in msg:
                        msg = msg[msg.find("numeric value:"):]
                        msg = msg[:msg.find("at")]
                    if "expected a valid value" in msg:
                        msg = msg[msg.find("expected a valid value"):]
                        msg = msg[:msg.find(")")]
                    if "was expecting" in msg:
                        msg = msg[msg.find("was expecting"):]
                        msg = msg[:msg.find(")")]
                    if "Expected " in msg:
                        msg = msg[msg.find("Expected"):]
                        msg = msg[:msg.find("at")]
                for path in msg_500:
                    if path[-1] != '/' and path + "/" in msg_500 and path + "/" in current_path:
                        if msg not in msg_500[path + "/"]:
                            print(msg)
                            msg_500[path + "/"].append(msg)
                    elif path in current_path:
                        if msg not in msg_500[path]:
                            print(msg)
                            msg_500[path].append(msg)
    for path in msg_500:
        request_500 += len(msg_500[path])
    for path in path_2xx:
        for op in path_2xx[path]:
            executed_operation += 1
            time_2xx += path_2xx[path][op]
    if executed_operation == 0:
        time_2xx = '-'
        executed_operation = '-'
    else:
        time_2xx = time_2xx / executed_operation
        req_2xx = req_2xx / executed_operation



    return request_total, request_2xx, request_4xx, request_500, executed_operation, time_2xx, req_2xx

a = [0,0,0,0,0,0,0]
b = [0,0,0,0,0,0,0]
c = [0,0,0,0,0,0,0]
d = [0,0,0,0,0,0,0]
e = [0,0,0,0,0,0,0]
ff = [0,0,0,0,0,0,0]
g = [0,0,0,0,0,0,0]
h = [0,0,0,0,0,0,0]
l = [0,0,0,0,0,0,0]



for i in range(1,2):
    it = str(i)
    print(it + " iteration is processing...")
    print("FDIC is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-fdic.txt", "fdic")
    a[0] += t1
    a[1] += t2
    a[2] += t3
    a[3] += t4
    if t7 != 0:
        a[4] += t5
        a[5] += t6
        a[6] += t7
    print("Genome-Nexus is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-genome-nexus.txt", "genome-nexus")
    b[0] += t1
    b[1] += t2
    b[2] += t3
    b[3] += t4
    if t7 != 0:
        b[4] += t5
        b[5] += t6
        b[6] += t7
    count_coverage("services/genome-nexus/", "9002")
    print("Language-tool is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-language-tool.txt", "language-tool")
    c[0] += t1
    c[1] += t2
    c[2] += t3
    c[3] += t4
    if t7 != 0:
        c[4] += t5
        c[5] += t6
        c[6] += t7
    count_coverage("services/emb/cs/rest/original/languagetool", "9003")
    print("OCVN is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-ocvn.txt", "ocvn")
    d[0] += t1
    d[1] += t2
    d[2] += t3
    d[3] += t4
    if t7 != 0:
        d[4] += t5
        d[5] += t6
        d[6] += t7
    count_coverage("services/emb/cs/rest-gui/ocvn", "9004")
    print("OhSome is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-ohsome.txt", "ohsome")
    e[0] += t1
    e[1] += t2
    e[2] += t3
    e[3] += t4
    if t7 != 0:
        e[4] += t5
        e[5] += t6
        e[6] += t7
    print("OMDB is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-omdb.txt", "omdb")
    ff[0] += t1
    ff[1] += t2
    ff[2] += t3
    ff[3] += t4
    if t7 != 0:
        ff[4] += t5
        ff[5] += t6
        ff[6] += t7
    print("Rest-countries is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-rest-countries.txt", "rest-countries")
    g[0] += t1
    g[1] += t2
    g[2] += t3
    g[3] += t4
    if t7 != 0:
        g[4] += t5
        g[5] += t6
        g[6] += t7
    print("Spotify is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-spotify.txt", "spotify")
    h[0] += t1
    h[1] += t2
    h[2] += t3
    h[3] += t4
    if t7 != 0:
        h[4] += t5
        h[5] += t6
        h[6] += t7
    print("YouTube is processing...")
    t1, t2, t3, t4, t5, t6, t7 = count_requests(it + "/log-youtube.txt", "youtube")
    l[0] += t1
    l[1] += t2
    l[2] += t3
    l[3] += t4
    if t7 != 0:
        l[4] += t5
        l[5] += t6
        l[6] += t7
    count_coverage("services/youtube", "9009")
res = str(a[0]/10) + ',' + str(a[1]/10) + ',' + str(a[2]/10) + ',' + str(a[3]/10) + ',' + str(a[4]/10) + ',' + str(a[5]/10) + ',' + str(a[6]/10) + '\n'


total_branch = 0
covered_branch = 0
total_line = 0
covered_line = 0
total_method = 0
covered_method = 0
for i in range(1,2):
    with open(str(i) + "/9002.csv") as f:
        lines = f.readlines()
        for line in lines:
            items = line.split(",")
            if '_COVERED' not in items[6] and '_MISSED' not in items[6]:
                covered_branch = covered_branch + int(items[6])
                total_branch = total_branch + int(items[6]) + int(items[5])
                covered_line = covered_line + int(items[8])
                total_line = total_line + int(items[8]) + int(items[7])
                covered_method = covered_method + int(items[12])
                total_method = total_method + int(items[12]) + int(items[11])
res = res + str(b[0]/10) + ',' + str(b[1]/10) + ',' + str(b[2]/10) + ',' + str(b[3]/10) + ',' + str(b[4]/10) + ',' + str(b[5]/10) + ',' + str(b[6]/10) + ',' + str(covered_branch / total_branch) + ',' + str(covered_line / total_line) + ',' + str(
    covered_method / total_method) + '\n'

total_branch = 0
covered_branch = 0
total_line = 0
covered_line = 0
total_method = 0
covered_method = 0
for i in range(1,2):

    with open(str(i) + "/9003.csv") as f:
        lines = f.readlines()
        for line in lines:
            items = line.split(",")
            if '_COVERED' not in items[6] and '_MISSED' not in items[6]:
                covered_branch = covered_branch + int(items[6])
                total_branch = total_branch + int(items[6]) + int(items[5])
                covered_line = covered_line + int(items[8])
                total_line = total_line + int(items[8]) + int(items[7])
                covered_method = covered_method + int(items[12])
                total_method = total_method + int(items[12]) + int(items[11])
res = res + str(c[0]/10) + ',' + str(c[1]/10) + ',' + str(c[2]/10) + ',' + str(c[3]/10) + ',' + str(c[4]/10) + ',' + str(c[5]/10) + ',' + str(c[6]/10) + ',' + str(covered_branch / total_branch) + ',' + str(covered_line / total_line) + ',' + str(
    covered_method / total_method) + '\n'

total_branch = 0
covered_branch = 0
total_line = 0
covered_line = 0
total_method = 0
covered_method = 0

for i in range(1,2):
    with open(str(i) + "/9004.csv") as f:
        lines = f.readlines()
        for line in lines:
            items = line.split(",")
            if '_COVERED' not in items[6] and '_MISSED' not in items[6]:
                covered_branch = covered_branch + int(items[6])
                total_branch = total_branch + int(items[6]) + int(items[5])
                covered_line = covered_line + int(items[8])
                total_line = total_line + int(items[8]) + int(items[7])
                covered_method = covered_method + int(items[12])
                total_method = total_method + int(items[12]) + int(items[11])
res = res + str(d[0]/10) + ',' + str(d[1]/10) + ',' + str(d[2]/10) + ',' + str(d[3]/10) + ',' + str(d[4]/10) + ',' + str(d[5]/10) + ',' + str(d[6]/10) + ',' + str(covered_branch / total_branch) + ',' + str(covered_line / total_line) + ',' + str(
    covered_method / total_method) + '\n'
res = res + str(e[0]/10) + ',' + str(e[1]/10) + ',' + str(e[2]/10) + ',' + str(e[3]/10) + ',' + str(e[4]/10) + ',' + str(e[5]/10) + ',' + str(e[6]/10) + '\n'
res = res + str(ff[0]/10) + ',' + str(ff[1]/10) + ',' + str(ff[2]/10) + ',' + str(ff[3]/10) + ',' + str(ff[4]/10) + ',' + str(ff[5]/10) + ',' + str(ff[6]/10) + '\n'
res = res + str(g[0]/10) + ',' + str(g[1]/10) + ',' + str(g[2]/10) + ',' + str(g[3]/10) + ',' + str(g[4]/10) + ',' + str(g[5]/10) + ',' + str(g[6]/10) + '\n'
res = res + str(h[0]/10) + ',' + str(h[1]/10) + ',' + str(h[2]/10) + ',' + str(h[3]/10) + ',' + str(h[4]/10) + ',' + str(h[5]/10) + ',' + str(h[6]/10) + '\n'

total_branch = 0
covered_branch = 0
total_line = 0
covered_line = 0
total_method = 0
covered_method = 0

for i in range(1,2):
    with open(str(i) + "/9009.csv") as f:
        lines = f.readlines()
        for line in lines:
            items = line.split(",")
            if '_COVERED' not in items[6] and '_MISSED' not in items[6]:
                covered_branch = covered_branch + int(items[6])
                total_branch = total_branch + int(items[6]) + int(items[5])
                covered_line = covered_line + int(items[8])
                total_line = total_line + int(items[8]) + int(items[7])
                covered_method = covered_method + int(items[12])
                total_method = total_method + int(items[12]) + int(items[11])
res = res + str(l[0]/10) + ',' + str(l[1]/10) + ',' + str(l[2]/10) + ',' + str(l[3]/10) + ',' + str(l[4]/10) + ',' + str(l[5]/10) + ',' + str(l[6]/10) + ',' + str(covered_branch / total_branch) + ',' + str(covered_line / total_line) + ',' + str(
    covered_method / total_method) + '\n'


with open("result.csv", "w") as f:
    f.write(res)

