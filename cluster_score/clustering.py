import multiprocessing as mp
import os
import sys

import pandas as pd
import rdkit
import rdkit.Chem as Chem
import rdkit.Chem.AllChem as AllChem
import tqdm
from rdkit import DataStructs
from rdkit.ML.Cluster import Butina

csv_file = sys.argv[1]
RA_path = sys.argv[2]
output_file = sys.argv[3]

smiles = pd.read_csv(csv_file)['SMILES']
mols = [Chem.MolFromSmiles(s) for s in smiles]


from RAscore import RAscore_XGB

scorer = RAscore_XGB.RAScorerXGB(os.path.join(RA_path, 'models/XGB_chembl_ecfp_counts/model.pkl'))


def save_prop(mol):
    prop = scorer.predict(Chem.MolToSmiles(mol))
    mol.SetProp('RA_xgb', str(prop))
    return mol

def clustering(mols):
    fps = [AllChem.GetMorganFingerprintAsBitVect(mols, 2, nBits=1024) \
            for mols in tqdm.tqdm(mols, desc='Generating Morgan Fingerprints')]
    dists = []
    nfps = len(fps)
    for i in range(1,nfps):
        sims = DataStructs.BulkTanimotoSimilarity(fps[i],fps[:i])
        dists.extend([1-x for x in sims])
        cs = Butina.ClusterData(dists,nfps, 0.4, isDistData=True)
    #convert cs into cluster id for each molecule
    cluster_id = [0]*nfps
    for i,cl in enumerate(cs):
        for j in cl:
            cluster_id[j] = i
    return cluster_id


if __name__ == '__main__':

    writer = Chem.SDWriter(output_file)
    print('Clustering...')
    cluster_id = clustering(mols)
    for m in tqdm.tqdm(mols, desc='Saving RA properties'):
        m = save_prop(m)
        writer.write(m)
    writer.close()
