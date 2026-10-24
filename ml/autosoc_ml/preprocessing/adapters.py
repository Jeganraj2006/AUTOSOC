import pandas as pd

class BaseAdapter:
    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

class UNSWNB15Adapter(BaseAdapter):
    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()
        out['duration'] = df['dur']
        out['proto_tcp'] = (df['proto'] == 'tcp').astype(int)
        out['proto_udp'] = (df['proto'] == 'udp').astype(int)
        out['fwd_pkts'] = df['Spkts']
        out['bwd_pkts'] = df['Dpkts']
        out['fwd_bytes'] = df['sbytes']
        out['bwd_bytes'] = df['dbytes']
        # Map label: 0 is benign, 1 is attack
        out['label'] = df['label'].apply(lambda x: 'attack' if x == 1 else 'benign')
        out['dataset_source'] = 'unsw_nb15'
        return out

class CICIDS2017Adapter(BaseAdapter):
    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()
        # Duration is in microseconds, convert to seconds to match UNSW
        out['duration'] = df['Flow Duration'] / 1e6
        # Protocol is not easily parsed as string in CICIDS2017 raw subset I generated, I'll default to 0
        out['proto_tcp'] = 0
        out['proto_udp'] = 0
        out['fwd_pkts'] = df['Total Fwd Packets']
        out['bwd_pkts'] = df['Total Backward Packets']
        out['fwd_bytes'] = df['Total Length of Fwd Packets']
        out['bwd_bytes'] = df['Total Length of Bwd Packets']
        out['label'] = df['Label'].apply(lambda x: 'benign' if x == 'BENIGN' else 'attack')
        out['dataset_source'] = 'cicids2017'
        return out

class CICIOT2023Adapter(BaseAdapter):
    def adapt(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame()
        out['duration'] = df['flow_duration']
        out['proto_tcp'] = df['TCP']
        out['proto_udp'] = df['UDP']
        out['fwd_pkts'] = 0 # Not cleanly mapped in this subset
        out['bwd_pkts'] = 0
        out['fwd_bytes'] = 0
        out['bwd_bytes'] = 0
        out['label'] = df['label'].apply(lambda x: 'benign' if 'Benign' in str(x) else 'attack')
        out['dataset_source'] = 'cic_iot_2023'
        return out
