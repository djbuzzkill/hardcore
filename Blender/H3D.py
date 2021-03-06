bl_info = {
    "name": "H3D Standalone",
    "author": "djbuzzkill",
    "blender": (2, 5, 7),
    "location": "File > Import-Export",
    "description": "H3D file writing ",
    "warning": "",
    "tracker_url": "",
    "support": "TESTING",
    "category": "Import-Export"
    }
 
import Dx
import mathutils
#
# H3D - is for Horde3D 
# 


#
# writes H3DG marker into file
def Write_H3DG_v5 (f): 
    'writes H3DG marker into file'
    H3DG = b'H3DG'
    Dx.write_char_array (f, H3DG, 4)
    Dx.write_u32 (f, 5)
    return 8

# writes H3DA marker into file
def Write_H3DA_v3 (f): 
    'writes H3DA marker into file'
    Dx.write_char_array (f, b'H3DA', 4)
    Dx.write_u32 (f, 3)
    return 8
    

#
# Write_geo () - write a Horde3D .geo file, this is the new one
# meshz - mesh list from Extract_mesh
# skel - armature object, meshs should reference this
def Write_geo  (fpath, meshz , skel): 
    
    f = open (fpath, "wb")

    # header
    Write_H3DG_v5 (f)
    
    nada = "nada"

    # joints - skeleton not supported yet
    # all we have to do here is write the matrices
    # in the order of the bone joint indices
    # 

    # writing inverse bind matrices
    arma_bone_map = {}
    if skel: 
        # inverse bind matrices
        Dx.write_u32 (f, len (skel.data.bones))
        for i, b in enumerate (skel.data.bones): 
            # bp = Dx.bone_relative_pos (v) <-- use this in the xml graph, but not here
            # not the relative , but absolute (in armature space)
            
            # swizzle coords Bl -> OpenGL
            #sw_pos = [b.head_local[1], b.head_local[2], b.head_local[0]]
            sw_pos = [b.tail_local[1], b.tail_local[2], b.tail_local[0]]
            invb = mathutils.Matrix.Translation (sw_pos)

            arma_bone_map[b.name] = i

            invb.invert () 
            invb.transpose ()
            Dx.write_mat44 (f, invb)

    else: 
        Dx.write_u32 (f, 0)


    print (arma_bone_map)

    # 
    n_Pos = 0; 
    n_Nrm = 0; 
    n_Txc0 = 0;
    n_Txc1 = 0;
    n_Tan = 0
    n_BiTan = 0
    n_JntI = 0
    n_JntW = 0

    # count total verts 
    for m in meshz: 
        if m.positions: 
            n_Pos = n_Pos + len (m.positions)
        if m.normals: 
            n_Nrm = n_Nrm + len (m.normals)
        if m.tangents: 
            n_Tan = n_Tan + len (m.tangents)
        if m.bi_Tangents: 
            n_BiTan = n_BiTan + len (m.bi_Tangents)
        if m.texcoord0: 
            n_Txc0 = n_Txc0 + len (m.texcoord0)
        if m.texcoord1: 
            n_Txc1 = n_Txc1 + len (m.texcoord1)
        if m.bone_Inds: 
            n_JntI = n_JntI + len (m.bone_Inds)
        if m.bone_Weights: 
            n_JntW = n_JntW + len (m.bone_Weights)


    # Num Vert Attribs 
    num_VertAttribs = 0
    if n_Pos > 0: 
        print (' include:positions')
        num_VertAttribs = 1 + num_VertAttribs
    if n_Nrm == n_Pos: 
        print (' include:normals')
        num_VertAttribs = 1 + num_VertAttribs 
    if n_Tan == n_Pos: 
        print (' include:tangents')
        num_VertAttribs = 1 + num_VertAttribs
    if n_BiTan == n_Pos: 
        print (' include:bitangents')
        num_VertAttribs = 1 + num_VertAttribs
    if n_Txc0 == n_Pos: 
        print (' include:texcoord0')
        num_VertAttribs = 1 + num_VertAttribs
    if n_Txc1 == n_Pos: 
        print (' include:texcoord1')
        num_VertAttribs = 1 + num_VertAttribs
    if n_JntI == n_Pos: 
        print (' include:jointinds')
        num_VertAttribs = 1 + num_VertAttribs
    if n_JntW == n_Pos: 
        print (' include:jointweights')
        num_VertAttribs = 1 + num_VertAttribs

    # numVertexStreams
    print ('num_VertAttribs:' + str (num_VertAttribs))
    Dx.write_s32 (f, num_VertAttribs)

    # numVertices - all should be same as pos's

    #
    # pos
    print ('n_Pos:' + str (n_Pos))
    Dx.write_s32 (f, n_Pos)
    if n_Pos > 0: 
        Dx.write_u32 (f, MgID_Position)
        Dx.write_u32 (f, 12) # 3 * sizeof(float)
        for m in meshz: 
            for p in m.positions:
                Dx.write_f32 (f, p[0])
                Dx.write_f32 (f, p[1])
                Dx.write_f32 (f, p[2])

    # normals
    print ('n_Nrm:' + str (n_Nrm))
    if n_Nrm == n_Pos: 
        Dx.write_u32 (f, MgID_Normal)
        Dx.write_u32 (f, 6) # 3 * sizeof(short)
        for m in meshz: 
            for n in m.normals: 
                Dx.write_s16 (f,  int (n[0] * 32767))
                Dx.write_s16 (f,  int (n[1] * 32767))
                Dx.write_s16 (f,  int (n[2] * 32767))
                
    # tangents
    # write_u32 (f, MgID_Tangent)
    
    # MgID_Bitangent = 3

    # tex crd 0
    print ('n_Txc0:' + str (n_Txc0))
    if n_Txc0 == n_Pos: 
        Dx.write_u32 (f, MgID_TexCoord0)
        Dx.write_u32 (f, 8) # 2 * sizeof(float)
        for m in meshz: 
            for tx in m.texcoord0: 
                Dx.write_f32 (f, tx[0])
                Dx.write_f32 (f, tx[1])

    # MgID_TexCoord1 = 7

    # Joint Indices
    print ('m.bone_Inds:'  + str (len (m.bone_Inds)))
    if n_JntI == n_Pos: 
        Dx.write_u32 (f, MgID_JointIndices)
        Dx.write_u32 (f, 4)
        for m in meshz: 
            for ji in m.bone_Inds: 


                assert (m.vg_map[ ji[0]] in arma_bone_map)
                assert (m.vg_map[ ji[1]] in arma_bone_map)
                assert (m.vg_map[ ji[2]] in arma_bone_map)
                assert (m.vg_map[ ji[3]] in arma_bone_map)

                Dx.write_u8 (f, arma_bone_map [m.vg_map[ ji[0]] ] )
                Dx.write_u8 (f, arma_bone_map [m.vg_map[ ji[1]] ] )
                Dx.write_u8 (f, arma_bone_map [m.vg_map[ ji[2]] ] )
                Dx.write_u8 (f, arma_bone_map [m.vg_map[ ji[3]] ] )
                # Dx.write_u8 (f, ji[0])
                # Dx.write_u8 (f, ji[1])
                # Dx.write_u8 (f, ji[2])
                # Dx.write_u8 (f, ji[3])

    

    # arma_bone_map :: name -> index

    # Joint Weights
    if n_JntW == n_Pos: 
        Dx.write_u32 (f, MgID_JointWeights)
        Dx.write_u32 (f, 4)
        for m in meshz: 
          
            for jw in m.bone_Weights:
                Dx.write_u8 (f, int (jw[0] * 255))
                Dx.write_u8 (f, int (jw[1] * 255))
                Dx.write_u8 (f, int (jw[2] * 255))
                Dx.write_u8 (f, int (jw[3] * 255))


    # indices
    Dx.write_u32 (f, sum ( [len(m.triindices) for m in meshz] ))
    vert_Count_accum = 0
    for m in meshz:
        for i in [vert_Count_accum + ti for ti in m.triindices]: 
            Dx.write_s32 (f, i)

        vert_Count_accum = vert_Count_accum + len (m.positions)

    # morph targets
    # dont do 
    num_MorphTargets = 0
    Dx.write_s32 (f, num_MorphTargets)
    
    # end Write_geo_data
    f.close ()

    return 'wrote .geo to: ' + fpath


#
#
#  Build_armature_graph_XML :: Bl Bone -> Joint
def Build_armature_graph_XML (b, ind_map): 
    
    j  = Dx.XML_node ('Joint')
        
    # b -starts off with the root
    vpos = Dx.bone_relative_pos (b)
    #vpos = [b.head_local[0], b.head_local[1], b.head_local[2] ]
    #vpos = [b.tail_local[0], b.tail_local[1], b.tail_local[2] ]
    
    j.attributes.extend ( 
        [
            ('name', b.name),
            ('jointIndex', str (ind_map[b])), 
            ('tx' , str (vpos[1])),
            ('ty' , str (vpos[2])), 
            ('tz' , str (vpos [0])),
            ('sx' , '1.0'), 
            ('sy' , '1.0'), 
            ('sz' , '1.0'), 
            ('rx' , '0.0'), 
            ('ry' , '0.0'), 
            ('rz' , '0.0')
            ]
        )
    

    for ch in b.children: 
        j.children.append (Build_armature_graph_XML (ch, ind_map))


    return j


#
# Build_Model_XML () - new .scene writing
def Build_Model_XML (mod_Name, geo_File, meshz, arma): 
    'generate XML nodes from meshes and armature'
    model = Dx.XML_node ('Model')
    model.attributes.extend  ([("name", mod_Name) , ("geometry", geo_File)])

    # 
    if  arma: 

        # ! we have a map<index, bone>, what do we do with it?
        boneID_map = {}
        IndexBone_map = {}
        for i, b, in enumerate (arma.data.bones):
            boneID_map[i] = b
            IndexBone_map[b] = i 
        

        # boneID_map[0] is the root
        joint_root = Build_armature_graph_XML (boneID_map[0], IndexBone_map)

        # joint = tx, ty, tz, rx, ry, rz, sx, sy, sz, jointID, 
        # skel_XML_root = build_xml_graph_for_armature (skel)



        model.children.append  (joint_root)
        pass 


    batchOffs_accum = 0
    vertOffs_accum = 0

    for m in meshz:  
        child = Dx.XML_node ('Mesh')
        batch_Len = len (m.triindices)
        vert_Len    = len (m.positions)

        child.attributes.extend ( 
            [
                ('name', m.name) , 
                ('material', m.material) , 
                ('batchStart', str (batchOffs_accum)), 
                ('batchCount', str(batch_Len)), 
                ('vertRStart', str (vertOffs_accum)), 
                ('vertREnd', str (vertOffs_accum + vert_Len - 1)), 
                ('tx', str (m.location[0])), 
                ('ty', str (m.location[1])), 
                ('tz', str (m.location[2]))
                ] 
            )
        batchOffs_accum = batchOffs_accum + batch_Len
        vertOffs_accum    = vertOffs_accum + vert_Len 
        model.children.append  (child)



    return model



#
# write a .scene XML file
# fname - 
# mode_Name - 
# geo_File - source of .geo
# meshs - same meshes used from Write_geo
# skel - same armature used from Write_geo
def Write_scene  (fname, mod_Name,  geo_File, meshs, skel): 
    model = Build_Model_XML (mod_Name, geo_File, meshs, skel)
    f = open (fname, 'w')
    Dx.Write_XML_node (f, model, 0)
    f.close ()


#
# Horde3D objects
#
def Make_anim_node (): 
    return { 
        'compressed' : false, 
        'rotation' : [], 
        'translation' : [], 
        'scale' : []
        }

#
def Make_anim_frame ():  
    return { 
        'vNodes' : {}
        }

#
def Make_anim (): 
    return { 
        'num_Animatios' : 0, 
        'num_Frames' : 0, 
        'vAnimationFrames' : []
        }

       
