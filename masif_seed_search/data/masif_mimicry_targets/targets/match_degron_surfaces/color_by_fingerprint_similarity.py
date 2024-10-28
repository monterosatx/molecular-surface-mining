from params_mimicry import params
import os 
import sys
import pymesh 
import numpy as np
from scipy.spatial import cKDTree
from IPython.core.debugger import set_trace

def process_patch(matchedsurf, matcheddesc, targetsurf, targetdesc, outfn):
    """ Open the file and compute the fingerprint similarity. """
    # for every point in the matched surface, compute the distance to the target surface.
    kdt = cKDTree(targetsurf.vertices)
    dist, idx = kdt.query(matchedsurf.vertices)

    # Compute the fingerprint similarity for every pair of matched vertices 
    # and target vertices.
    matched_fingerprints = matcheddesc
    target_fingerprints = targetdesc[idx]
    desc_dists = np.linalg.norm(matched_fingerprints - target_fingerprints, axis=1)
    # desc_dists are values mainly between 2 and 4; clip them to the range [2,4] and then normalize to 0,1
    desc_dists = np.clip(desc_dists, 2, 4)
    desc_dists = (desc_dists - 2) / 2
    # Compute the similarity as 1 - distance.
    similarity = 1 - desc_dists

    # Compute the surface similarity for every pair of matched vertices and target vertices.
    nx = matchedsurf.get_attribute("vertex_nx")
    ny = matchedsurf.get_attribute("vertex_ny")
    nz = matchedsurf.get_attribute("vertex_nz")
    n1 = np.vstack((nx, ny, nz)).T

    nx = targetsurf.get_attribute("vertex_nx")
    ny = targetsurf.get_attribute("vertex_ny")
    nz = targetsurf.get_attribute("vertex_nz")
    n2 = np.vstack((nx, ny, nz)).T

    w = 0.25
    #meshout =  pymesh.form_mesh(mesh1.vertices, mesh1.faces)
    comp1 = [np.dot(n1[x], n2[idx[x]]) for x in range(len(idx))]
    comp1 = np.multiply(comp1, np.exp(-w * np.square(dist)))
    comp1[comp1 < 1e-4] = 0

    # Save the matched surface with the similarity as a vertex_iface
    matchedsurf.set_attribute("vertex_iface", similarity)
    # remove duplicated vertex_x, vertex_y, vertex_z
    if "vertex_x" in matchedsurf.get_attribute_names():
        matchedsurf.remove_attribute("vertex_x")
        matchedsurf.remove_attribute("vertex_y")
        matchedsurf.remove_attribute("vertex_z")
    
    matchedsurf.set_attribute("vertex_hbond", comp1)
    
    pymesh.save_mesh(outfn, matchedsurf, *matchedsurf.get_attribute_names(), use_float=True, ascii=True)
    
outdir = params['out_dir_template']
target = sys.argv[1]

newpath = os.path.join(outdir.format(target))

target_surf = pymesh.load_mesh(os.path.join(params['target_ply_iface_dir'], target)+'.ply')
target_desc = np.load(os.path.join(params['target_desc_dir'], target)+'/p1_desc_straight.npy')

if os.path.isdir(newpath): 
    for site in os.listdir(newpath): 
        sitepath = os.path.join(newpath, site)
        if os.path.isdir(sitepath): 
            for matchedtarget in os.listdir(sitepath): 
                print('Processing ', matchedtarget)
                matchedtargetpath = os.path.join(sitepath, matchedtarget)
                if os.path.isdir(matchedtargetpath): 
                    matchedtarget_desc = np.load(params['seed_desc_dir'] + '/'+matchedtarget+'/p1_desc_straight.npy')                

                    for patch in os.listdir(matchedtargetpath): 
                        if patch.endswith('.ply') and 'desc_dist' not in patch and 'patch' not in patch: 
                            outfn = os.path.join(matchedtargetpath, patch.replace('.ply', 'desc_dist.ply'))
                            matchedsurf = pymesh.load_mesh(os.path.join(matchedtargetpath, patch))
                            process_patch(matchedsurf, matchedtarget_desc, target_surf, target_desc, outfn)
                            outfn = os.path.join(matchedtargetpath, patch.replace('.ply', 'desc_dist_rev.ply'))
                            process_patch(target_surf, target_desc, matchedsurf, matchedtarget_desc, outfn)
                               
