import { http, HttpResponse } from 'msw'

export const handlers = [
    http.post<{}, {server: string, ipv6_measurement: boolean}, {measurement: any[]} | { detail: string }>(
        '/measurements/', async ({request: req}) => {
            const body = await req.json()
            const mockMeasurement: any[] = [
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.94.203.168",
                    "ntp_server_ip": "17.253.52.253",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "NL",
                        "coordinates": [
                        52.3824,
                        4.8995
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3959231207,
                        "fraction": 3938824192
                    },
                    "server_recv_time": {
                        "seconds": 3959231202,
                        "fraction": 60612608
                    },
                    "server_sent_time": {
                        "seconds": 3959231202,
                        "fraction": 60737536
                    },
                    "client_recv_time": {
                        "seconds": 3959231207,
                        "fraction": 3962165248
                    },
                    "offset": -5.905669212341309,
                    "rtt": 0.005405426025390625,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001678466796875,
                    "ntp_last_sync_time": {
                        "seconds": 3959231196,
                        "fraction": 2094338048
                    },
                    "leap": 0,
                    "jitter": 0.8551980300704615,
                    "nr_measurements_jitter": 8
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.94.203.168",
                    "ntp_server_ip": "17.253.14.125",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "DE",
                        "coordinates": [
                        50.1169,
                        8.6837
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3959231207,
                        "fraction": 4003549184
                    },
                    "server_recv_time": {
                        "seconds": 3959231202,
                        "fraction": 152694784
                    },
                    "server_sent_time": {
                        "seconds": 3959231202,
                        "fraction": 152760320
                    },
                    "client_recv_time": {
                        "seconds": 3959231207,
                        "fraction": 4076879872
                    },
                    "offset": -5.905126094818115,
                    "rtt": 0.017058372497558594,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001373291015625,
                    "ntp_last_sync_time": {
                        "seconds": 3959231198,
                        "fraction": 2253635584
                    },
                    "leap": 0,
                    "jitter": 1.5482209225207348,
                    "nr_measurements_jitter": 8
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.94.203.168",
                    "ntp_server_ip": "17.253.52.125",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "NL",
                        "coordinates": [
                        52.3824,
                        4.8995
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3959231207,
                        "fraction": 4114880512
                    },
                    "server_recv_time": {
                        "seconds": 3959231202,
                        "fraction": 253331456
                    },
                    "server_sent_time": {
                        "seconds": 3959231202,
                        "fraction": 253396992
                    },
                    "client_recv_time": {
                        "seconds": 3959231207,
                        "fraction": 4163008512
                    },
                    "offset": -5.904682159423828,
                    "rtt": 0.011190414428710938,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001068115234375,
                    "ntp_last_sync_time": {
                        "seconds": 3959231200,
                        "fraction": 3654258688
                    },
                    "leap": 0,
                    "jitter": 0.8562105498953563,
                    "nr_measurements_jitter": 8
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.94.203.168",
                    "ntp_server_ip": "17.253.28.123",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "GB",
                        "coordinates": [
                        51.5177,
                        -0.6215
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3959231207,
                        "fraction": 4202512384
                    },
                    "server_recv_time": {
                        "seconds": 3959231202,
                        "fraction": 390150144
                    },
                    "server_sent_time": {
                        "seconds": 3959231202,
                        "fraction": 390213632
                    },
                    "client_recv_time": {
                        "seconds": 3959231208,
                        "fraction": 24203264
                    },
                    "offset": -5.901208162307739,
                    "rtt": 0.02714681625366211,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.00018310546875,
                    "ntp_last_sync_time": {
                        "seconds": 3959231196,
                        "fraction": 3131183104
                    },
                    "leap": 0,
                    "jitter": 0,
                    "nr_measurements_jitter": 1
                    }
                ]

            if(body.server === "time.apple.com"){
                return HttpResponse.json({measurement: mockMeasurement}, {status: 200})
            } else {
                return HttpResponse.json(
                    { detail: "Server is not reachable." },
                    { status: 503 }
                )
            }
        }
    ),
    http.get<{server: string, start: string, end: string}, never, {measurements: any[]} | {detail: string}>(
        '/measurements/history/', ({request}) => {
            const url = new URL(request.url, 'http://localhost')
            const start = url.searchParams.get('start')
            const end = url.searchParams.get('end')

            const mockHistoricalMeasurement = [
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.90.49.147",
                    "ntp_server_ip": "17.253.52.253",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "NL",
                        "coordinates": [
                        52.3824,
                        4.8995
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3958798919,
                        "fraction": 4197421056
                    },
                    "server_recv_time": {
                        "seconds": 3958798913,
                        "fraction": 939790336
                    },
                    "server_sent_time": {
                        "seconds": 3958798913,
                        "fraction": 939862016
                    },
                    "client_recv_time": {
                        "seconds": 3958798919,
                        "fraction": 4230189056
                    },
                    "offset": -6.762282609939575,
                    "rtt": 0.007612705230712891,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001678466796875,
                    "ntp_last_sync_time": {
                        "seconds": 3958798908,
                        "fraction": 2094313472
                    },
                    "leap": 0,
                    "jitter": null,
                    "nr_measurements_jitter": 0
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.90.49.147",
                    "ntp_server_ip": "17.253.14.123",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "DE",
                        "coordinates": [
                        50.1169,
                        8.6837
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3958798919,
                        "fraction": 4264443904
                    },
                    "server_recv_time": {
                        "seconds": 3958798913,
                        "fraction": 1021216768
                    },
                    "server_sent_time": {
                        "seconds": 3958798913,
                        "fraction": 1021317120
                    },
                    "client_recv_time": {
                        "seconds": 3958798920,
                        "fraction": 35274752
                    },
                    "offset": -6.762770891189575,
                    "rtt": 0.015296459197998047,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001983642578125,
                    "ntp_last_sync_time": {
                        "seconds": 3958798906,
                        "fraction": 645177344
                    },
                    "leap": 0,
                    "jitter": null,
                    "nr_measurements_jitter": 0
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.90.49.147",
                    "ntp_server_ip": "17.253.52.125",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "NL",
                        "coordinates": [
                        52.3824,
                        4.8995
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3958798920,
                        "fraction": 70766592
                    },
                    "server_recv_time": {
                        "seconds": 3958798913,
                        "fraction": 1108938752
                    },
                    "server_sent_time": {
                        "seconds": 3958798913,
                        "fraction": 1109004288
                    },
                    "client_recv_time": {
                        "seconds": 3958798920,
                        "fraction": 103895040
                    },
                    "offset": -6.7621307373046875,
                    "rtt": 0.00769805908203125,
                    "stratum": 1,
                    "precision": -20,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.000213623046875,
                    "ntp_last_sync_time": {
                        "seconds": 3958798904,
                        "fraction": 3654199296
                    },
                    "leap": 0,
                    "jitter": null,
                    "nr_measurements_jitter": 0
                    },
                    {
                    "ntp_version": 4,
                    "vantage_point_ip": "145.90.49.147",
                    "ntp_server_ip": "17.253.14.251",
                    "ntp_server_name": "time.apple.com",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "DE",
                        "coordinates": [
                        50.1169,
                        8.6837
                        ]
                    },
                    "ntp_server_ref_parent_ip": null,
                    "ref_name": "GPSs",
                    "client_sent_time": {
                        "seconds": 3958798920,
                        "fraction": 134465536
                    },
                    "server_recv_time": {
                        "seconds": 3958798913,
                        "fraction": 1186314240
                    },
                    "server_sent_time": {
                        "seconds": 3958798913,
                        "fraction": 1186375680
                    },
                    "client_recv_time": {
                        "seconds": 3958798920,
                        "fraction": 194453504
                    },
                    "offset": -6.762073755264282,
                    "rtt": 0.01395273208618164,
                    "stratum": 1,
                    "precision": -21,
                    "reachability": "",
                    "root_delay": 0,
                    "poll": 6,
                    "root_dispersion": 0.0001678466796875,
                    "ntp_last_sync_time": {
                        "seconds": 3958798907,
                        "fraction": 2075832320
                    },
                    "leap": 0,
                    "jitter": null,
                    "nr_measurements_jitter": 0
                    }
                ]

            if (start && end){
                const startDate = new Date(start)
                const endDate = new Date(end)
                if(startDate > endDate)
                    return HttpResponse.json({
                        "detail": "'start' must be earlier than 'end'"
                    },{status:400})
            }

            return HttpResponse.json({measurements: mockHistoricalMeasurement}, {status: 200})
        }
    ),
    http.post<{}, {server: string, ipv6_measurement: boolean}, {
        measurement_id?: string;
        vantage_point_ip?: string;
        vantage_point_location?: { country_code: string; coordinates: [number, number] };
        status?: string;
        message?: string;
        detail?: string;
    }>(
        'http://localhost:8000/measurements/ripe/trigger/', async ({request: req}) => {
            const {server} = await req.json()
            if (server === "time.apple.com"){
                return HttpResponse.json({
                    "measurement_id": "110405699",
                    "vantage_point_ip": "145.94.203.168",
                    "vantage_point_location": {
                        "country_code": "NL",
                        "coordinates": [
                        52.0038,
                        4.3733
                        ]
                    },
                    "status": "started",
                    "message": "You can fetch the result at /measurements/ripe/{measurement_id}"
                }, { status: 200 })
            }
            else {
                return HttpResponse.json({
                    detail:
                    "Ripe measurement initiated, but it failed: {'detail': 'There was a problem with your request', 'status': 400, 'title': 'Bad Request', 'code': 102, 'errors': [{'source': {'pointer': '/definitions'}, 'detail': 'This target cannot be resolved'}]}",
                },
                { status: 400 }
            )
            }
        }
    ),
    http.get<{measurement_id: string}, never, { status: string, message: string, results: any[]} | {detail: string}>(
        'http://localhost:8000/measurements/ripe/:measurement_id', ({params}) => {
            const measurementId = params.measurement_id
            const mockRipeMeasurement = {
                "status": "complete",
                "message": "Measurement has been completed.",
                "results": [
                    {
                    "ntp_version": 4,
                    "ripe_measurement_id": 110405699,
                    "ntp_server_ip": "17.253.52.125",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "NL",
                        "coordinates": [
                        52.3824,
                        4.8995
                        ]
                    },
                    "ntp_server_name": "time.apple.com",
                    "vantage_point_ip": "88.202.166.71",
                    "probe_addr": {
                        "ipv4": "88.202.166.71",
                        "ipv6": "2a04:8400:c300:ba00:ea94:f6ff:fe48:5f64"
                    },
                    "probe_id": "22138",
                    "probe_location": {
                        "country_code": "NL",
                        "coordinates": [
                        4.3685,
                        52.0015
                        ]
                    },
                    "time_to_result": 30.280227,
                    "stratum": 1,
                    "poll": 64,
                    "precision": 9.53674e-7,
                    "root_delay": 0,
                    "root_dispersion": 0.00018310477025806904,
                    "ref_id": "GPSs",
                    "probe_count_per_type": {
                        "asn": 9,
                        "prefix": 1,
                        "country": 26,
                        "area": 4,
                        "random": 0
                    },
                    "result": [
                        {
                        "client_sent_time": {
                            "seconds": 3959232158,
                            "fraction": 4123875328
                        },
                        "server_recv_time": {
                            "seconds": 3959232158,
                            "fraction": 3914455040
                        },
                        "server_sent_time": {
                            "seconds": 3959232158,
                            "fraction": 3914508288
                        },
                        "client_recv_time": {
                            "seconds": 3959232158,
                            "fraction": 4132907008
                        },
                        "rtt": 0.00209,
                        "offset": 0.049805
                        }
                    ]
                    },
                    {
                    "ntp_version": 4,
                    "ripe_measurement_id": 110405699,
                    "ntp_server_ip": "17.253.14.251",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "DE",
                        "coordinates": [
                        50.1169,
                        8.6837
                        ]
                    },
                    "ntp_server_name": "time.apple.com",
                    "vantage_point_ip": "91.215.7.190",
                    "probe_addr": {
                        "ipv4": "91.215.7.190",
                        "ipv6": null
                    },
                    "probe_id": "50350",
                    "probe_location": {
                        "country_code": "NL",
                        "coordinates": [
                        4.3595,
                        52.0075
                        ]
                    },
                    "time_to_result": 3.868,
                    "stratum": 1,
                    "poll": 64,
                    "precision": 4.76837e-7,
                    "root_delay": 0,
                    "root_dispersion": 0.000152587890625,
                    "ref_id": "GPSs",
                    "probe_count_per_type": {
                        "asn": 9,
                        "prefix": 1,
                        "country": 26,
                        "area": 4,
                        "random": 0
                    },
                    "result": [
                        {
                        "client_sent_time": {
                            "seconds": 3959232160,
                            "fraction": 1071108096
                        },
                        "server_recv_time": {
                            "seconds": 3959232159,
                            "fraction": 2370416640
                        },
                        "server_sent_time": {
                            "seconds": 3959232159,
                            "fraction": 2370535424
                        },
                        "client_recv_time": {
                            "seconds": 3959232160,
                            "fraction": 1108856832
                        },
                        "rtt": 0.008761,
                        "offset": 0.701862
                        }
                    ]
                    },
                    {
                    "ntp_version": 4,
                    "ripe_measurement_id": 110405699,
                    "ntp_server_ip": "17.253.14.253",
                    "ntp_server_location": {
                        "ip_is_anycast": false,
                        "country_code": "DE",
                        "coordinates": [
                        50.1169,
                        8.6837
                        ]
                    },
                    "ntp_server_name": "time.apple.com",
                    "vantage_point_ip": "145.94.58.246",
                    "probe_addr": {
                        "ipv4": "145.94.58.246",
                        "ipv6": "2001:610:908:c132:da58:d7ff:fe03:41a"
                    },
                    "probe_id": "61331",
                    "probe_location": {
                        "country_code": "NL",
                        "coordinates": [
                        4.3685,
                        51.9975
                        ]
                    },
                    "time_to_result": 0.969981,
                    "stratum": 1,
                    "poll": 64,
                    "precision": 9.53674e-7,
                    "root_delay": 0,
                    "root_dispersion": 0.00016784691251814365,
                    "ref_id": "GPSs",
                    "probe_count_per_type": {
                        "asn": 9,
                        "prefix": 1,
                        "country": 26,
                        "area": 4,
                        "random": 0
                    },
                    "result": [
                        {
                        "client_sent_time": {
                            "seconds": 3959232159,
                            "fraction": 1762224128
                        },
                        "server_recv_time": {
                            "seconds": 3959232159,
                            "fraction": 1777287168
                        },
                        "server_sent_time": {
                            "seconds": 3959232159,
                            "fraction": 1777362944
                        },
                        "client_recv_time": {
                            "seconds": 3959232159,
                            "fraction": 1797818368
                        },
                        "rtt": 0.008269,
                        "offset": 0.000628
                        }
                    ]
                    }
                ]
            }
            if(measurementId === "failed-retry") {
                return HttpResponse.json(
                    {
                    detail:
                        "Measurement retry",
                    },
                    { status: 405 }
                )
            }
            if (measurementId === 'failed-error') {
                return HttpResponse.json(
                    {
                    detail:
                        "Measurement failed",
                    },
                    { status: 500 }
                )
            }
            if (measurementId === 'failed-timeout') {
                return HttpResponse.json(
                    {
                    detail:
                        "Measurement failed",
                    },
                    { status: 504 }
                )
            }
            const measurementVariations = new Map<string, Partial<typeof mockRipeMeasurement>>([
                ["1",{status: "complete", message: "Measurement complete"}],
                ["2",{status: "partial_results", message: "Measurement ongoing"}],
                ["3",{status: "timeout", message: "Measurement timed out"}],
                ["4",{status: "pending", message: "Measurement pending"}],
                ["5",{status: "error", message: "Measurement error"}],
            ])
            const variation = measurementVariations.get(measurementId)
            const measurement = {...mockRipeMeasurement,...variation}

            return HttpResponse.json({status:measurement.status, message: measurement.message, results: measurement.results}, {status: 200})
        }
    )
]