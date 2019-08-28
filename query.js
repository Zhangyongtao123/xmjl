var fs = require('fs')
const hbase = require('hbase')
const Database = 'test2'
const client = new hbase.Client({
    host: '127.0.0.1',
    port: 7990
})

exports.get_single = function (req, res, next) {
    if (get_single_check(req.query) == false) {
        res.status(400).send("wrong query")
    } else {
        console.log('------get single vehicle info------')
        var startRow = req.query.VIN + '_' + req.query.start
        var endRow = req.query.VIN + '_' + req.query.end
        var column = req.query.type //type should be like tbox:vehi_speed
        console.log(startRow)
        console.log(endRow)
        console.log(column)
        try {
            client
                .table(Database)
                .scan({
                    startRow: startRow,
                    endRow: endRow,
                    column: column,
                    maxVersions: 1
                }, (err, rows) => {
                    if (err) {
                        console.log(err)
                        res.status(400).end()
                    } else {
                        console.log(rows)
			if (rows.length > 2000){
			    res.status(200).send(rows.slice(-2000))
			} else {
                            res.status(200).send(rows)
			}
                    }
                })
        } catch (error) {
            console.log(error)
            res.status(404).end()
        }
    }
};

//not yet
exports.get_all = function (req, res, next) {
    try {
        client.tables((error, tables) => {
            if (error) {
                console.log(error)
                res.end()
            } else {
                console.info(tables)
                res.status(200).send(tables)
            }
        })
    } catch (error) {
        res.status(404).end()
    }
};

exports.post_multi = function (req, res, next) {
    if (post_multi_check(req.body) == false) {
        res.status(400).send("wrong query")
    } else {
        console.log('------get multi vehicle info------')

        var column = req.body.type // type should be []
        var res_msg = []

        for (let index = 0; index < req.body.VIN.length; index++) {
            const VINs = req.body.VIN[index];

            var startRow = VINs + '_' + req.body.start
            var endRow = VINs + '_' + req.body.end
            //console.log(startRow)
            //console.log(endRow)
            //console.log(column)
            try {
                client
                    .table(Database)
                    .scan({
                        startRow: startRow,
                        endRow: endRow,
                        column: column,
                        maxVersions: 1
                    }, (err, rows) => {
                        if (err) {
                            console.log(err)
                            res.status(400).end()
                        } else {
                            //console.log(res_msg)
                            res_msg.push(rows)
                            console.log(index)
                            if (res_msg.length == req.body.VIN.length) {
                                console.log(res_msg)
                                res.status(200).send(res_msg)
                            }
                        }
                    })
            } catch (error) {
                console.log(error)
                res.status(404).end()
            }
        }
    }
};

exports.get_list = function (req, res, next) {
    var all_list = []
    try {
        fs.readFile('../global_list_mat.json', function (err, data) {
            if (err) {
                return console.error(err);
            }
            console.log("异步读取文件数据: " + data.toString());
            all_list.push(data.toString())
            fs.readFile('../global_list_tbx.json', function (err, data) {
                if (err) {
                    return console.error(err);
                }
                console.log("异步读取文件数据: " + data.toString());
                all_list.push(data.toString())
                console.log(all_list)
                res.status(200).send(all_list)
            });
        });
    } catch (error) {
        res.status(404).end()
    }
};

exports.get_current = function (req, res, next) {
    try {
        client.tables((error, tables) => {
            if (error) {
                console.log(error)
                res.end()
            } else {
                console.info(tables)
                res.status(200).send(tables)
            }
        })
    } catch (error) {
        res.status(404).end()
    }
};

//测试接口，列出所有表的信息
exports.get_all_table = function (req, res, next) {
    console.log('get all table')
    try {
        client.tables((error, tables) => {
            if (error) {
                console.log(error)
                res.end()
            } else {
                console.info(tables)
                res.status(200).send(tables)
            }
        })
    } catch (error) {
        res.status(404).end()
    }
};

//测试接口，扫描全表
exports.scan_table = function (req, res, next) {
    console.log('scan table')
    try {
        client
            .table(Database)
            .scan({
                //startRow: '1566613797101',
                maxVersions: 1
            }, (err, rows) => {
                if (err) {
                    res.status(400).end()
                } else {
                    console.info(rows)
                    res.status(200).send(rows)
                }
            })
    } catch (error) {
        res.status(404).end()
    }
};


var get_single_check = function (query) {
    console.log(query)
    if (query.VIN.length && query.start && query.end && query.type) {
        if (query.start <= query.end) {
            return true
        }
        console.log('start time should be smaller than end time')
        return false
    }
    console.log('request incomplete')
    return false
}

var post_multi_check = function (query) {
    console.log(query)
    if (query.VIN && query.start && query.end && query.type) {
        if (query.start <= query.end) {
            if (query.type.length > 0 && query.VIN.length > 0) {
                return true
            } else {
                console.log('query.type and query.VIN should be not empty []')
                return false
            }
        } else {
            console.log('start time should be smaller than end time')
            return false
        }
    }
    console.log('request incomplete')
    return false
}
