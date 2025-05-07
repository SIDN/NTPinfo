export type NTPData = {
    offset: number;
    delay: number;
    stratum: number;
    jitter: number;
    reachability: number;
    passing: boolean;
    time: number; //time at which the measurement was taken
  }