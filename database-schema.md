### Database design

The design for the two tables used to store data are as follows:
> * **measurements**  
>
>    * id -                      `bigint`, **Non-nullable**, ***primary key***, key to identify each measurement
>    * ntp_server_ip -           `inet`, the IP adress of the NTP server that was measured. Supports IPv4 or IPv6.
>    * ntp_server_name -         `text`, the name of the NTP server that was measured.
>    * ntp_version -             `smallint`, the version of NTP used for the measurement.
>    * ntp_server_ref_parent -   `inet`, the IPv4 or IPv6 adress of the parent of the NTP server.
>    * ref_name -                `text`, the name of the server the measured NTP server references.
>    * time_id -                 `bigint`,
>    * time_offset -             `double precision`,
>    * delay -                   `double precistion`, the delay of the NTP server.
>    * stratum -                 `integer`, the stratum the NTP server operates on.
>    * precision -               `double precision`, the precistion of the NTP server.
>    * reachability -            `text`, the status of the NTP server, made in accordance to the RCF8663 standard.
>    * root_delay -              `bigint`,
>    * ntp_last_sync_time -      `bigint`,
>    * root_delay_prec -         `bigint`,
>    * ntp_last_sync_time -      `bigint`,
>* **times**
>
>  * id -                      `bigint`, **Non-nullable**, ***primary key***, key to identify each measurement
>  * client_sent -             `bigint`, the time the request was sent by the client in Epoch time.
>  * client_sent_prec -        `bigint`, the 32 bits of accuracy for the client sent time.
>  * server_recv -             `bigint`, the time the request was received by the server in Epoch time.
>  * server_recv_prec -        `bigint`, the 32 bits of accuracy for the server receive time.
>  * server_sent -             `bigint`, the time when the request was sent back by the server in Epoch time.
>  * server_sent_prec -        `bigint`, the 32 bits of accuracy for the server send back time.
>  * client_recv -             `bigint`, the time when the request was received back by the client in Epoch time.
>  * client_recv_prec -        `bigint`, the 32 bits of accuracy for the client receive back time.
