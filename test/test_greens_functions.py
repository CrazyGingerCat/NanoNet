import sys
import matplotlib.pyplot as plt
import numpy as np
import tb


np.warnings.filterwarnings('ignore')


def simple_chain_greens_function(energy, h_0, h_r):
    G = (energy - h_0) / (2 * h_r ** 2)

    for j, E in enumerate(energy):
        if E - h_0 <= -2 * h_r:
            G[0, j] = G[0, j] + 1.0 / (2 * h_r ** 2) * np.sqrt((E - h_0) ** 2 - 4 * h_r ** 2)
        elif E - h_0 >= 2 * h_r:
            G[0, j] = G[0, j] - 1.0 / (2 * h_r ** 2) * np.sqrt((E - h_0) ** 2 - 4 * h_r ** 2)
        else:
            G[0, j] = G[0, j] - 1.0j / (2 * h_r ** 2) * np.sqrt(4 * h_r ** 2 - (E - h_0) ** 2)

    return G


def test_gf_single_atom_chain():
    sys.path.insert(0, '/home/mk/TB_project/tb')

    a = tb.Atom('A')
    a.add_orbital('s', 0.7)
    tb.Atom.orbital_sets = {'A': a}
    tb.set_tb_params(PARAMS_A_A={'ss_sigma': 0.5})

    xyz_file = """1
    H cell
    A1       0.0000000000    0.0000000000    0.0000000000
    """

    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=1.1)
    h.initialize()
    h.set_periodic_bc([[0, 0, 1.0]])
    h_l, h_0, h_r = h.get_coupling_hamiltonians()

    energy = np.linspace(-3.0, 3.0, 300)

    sgf_l = []
    sgf_r = []

    for E in energy:
        L, R = tb.surface_greens_function(E, h_l, h_0, h_r)
        sgf_l.append(L)
        sgf_r.append(R)

    sgf_l = np.array(sgf_l)
    sgf_r = np.array(sgf_r)

    num_sites = h_0.shape[0]
    gf = np.linalg.pinv(np.multiply.outer(energy, np.identity(num_sites)) - h_0 - sgf_l - sgf_r)

    np.testing.assert_allclose(sgf_l, sgf_r, atol=1e-9)
    expected = h_l * simple_chain_greens_function(energy, h_0, h_r) * h_r
    np.testing.assert_allclose(np.squeeze(sgf_r), np.squeeze(expected), atol=1e-5)


def test_gf_complex_chain():
    sys.path.insert(0, '/home/mk/TB_project/tb')

    a = tb.Atom('A')
    a.add_orbital('s', -0.7)
    b = tb.Atom('B')
    b.add_orbital('s', -0.5)
    c = tb.Atom('C')
    c.add_orbital('s', -0.3)

    tb.Atom.orbital_sets = {'A': a, 'B': b, 'C': c}

    tb.set_tb_params(PARAMS_A_A={'ss_sigma': -0.5},
                     PARAMS_B_B={'ss_sigma': -0.5},
                     PARAMS_A_B={'ss_sigma': -0.5},
                     PARAMS_B_C={'ss_sigma': -0.5},
                     PARAMS_A_C={'ss_sigma': -0.5})

    xyz_file = """4
    H cell
    A1       0.0000000000    0.0000000000    0.0000000000
    B2       0.0000000000    0.0000000000    1.0000000000
    A2       0.0000000000    1.0000000000    0.0000000000
    B3       0.0000000000    1.0000000000    1.0000000000
    """

    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=1.1)
    h.initialize()
    h.set_periodic_bc([[0, 0, 2.0]])
    h_l, h_0, h_r = h.get_coupling_hamiltonians()

    energy = np.linspace(-3.0, 1.5, 700)

    sgf_l = []
    sgf_r = []

    for E in energy:
        L, R = tb.surface_greens_function(E, h_l, h_0, h_r)
        sgf_l.append(L)
        sgf_r.append(R)

    sgf_l = np.array(sgf_l)
    sgf_r = np.array(sgf_r)

    num_sites = h_0.shape[0]
    gf = np.linalg.pinv(np.multiply.outer(energy, np.identity(num_sites)) - h_0 - sgf_l - sgf_r)

    tr = np.zeros((energy.shape[0]))
    dos = np.zeros((energy.shape[0]))

    for j, E in enumerate(energy):
        gf0 = np.matrix(gf[j, :, :])
        gamma_l = 1j * (np.matrix(sgf_l[j, :, :]) - np.matrix(sgf_l[j, :, :]).H)
        gamma_r = 1j * (np.matrix(sgf_r[j, :, :]) - np.matrix(sgf_r[j, :, :]).H)
        tr[j] = np.real(np.trace(gamma_l * gf0 * gamma_r * gf0.H))
        dos[j] = np.real(np.trace(1j * (gf0 - gf0.H)))

    np.testing.assert_allclose(dos, expected_dos_of_complex_chain(), atol=1e-5)
    np.testing.assert_allclose(tr, expected_tr_of_complex_chain(), atol=1e-5)


def expected_dos_of_complex_chain():
    return np.array([0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     3.01557668e+01, 2.12431628e+01, 1.73549661e+01, 1.50546970e+01,
                     1.34936744e+01, 1.23469171e+01, 1.14594544e+01, 1.07470171e+01,
                     1.01592991e+01, 9.66411021e+00, 9.23981348e+00, 8.87125543e+00,
                     8.54748646e+00, 8.26028142e+00, 8.00343558e+00, 7.77211694e+00,
                     7.56251282e+00, 7.37154150e+00, 7.19673588e+00, 7.03603528e+00,
                     6.88774655e+00, 6.75044185e+00, 6.62291742e+00, 6.50416113e+00,
                     6.39327219e+00, 6.28950516e+00, 6.19219714e+00, 6.10077568e+00,
                     6.01473253e+00, 5.93362650e+00, 5.85705988e+00, 5.78468335e+00,
                     5.71618940e+00, 5.65129348e+00, 5.58975081e+00, 5.53133541e+00,
                     5.47583970e+00, 5.42308164e+00, 5.37289521e+00, 5.32512677e+00,
                     5.27963907e+00, 5.23630460e+00, 5.19500798e+00, 5.15564367e+00,
                     5.11811529e+00, 5.08232650e+00, 5.04820504e+00, 5.01566986e+00,
                     4.98465014e+00, 4.95508415e+00, 4.92690972e+00, 4.90007174e+00,
                     4.87452109e+00, 4.85020914e+00, 4.82709191e+00, 4.80513008e+00,
                     4.78428497e+00, 4.76452029e+00, 4.74580721e+00, 4.72811337e+00,
                     4.71141266e+00, 4.69568025e+00, 4.68089293e+00, 4.66702617e+00,
                     4.65406192e+00, 4.64198548e+00, 4.63077657e+00, 4.62042217e+00,
                     4.61090925e+00, 4.60222297e+00, 4.59435722e+00, 4.58729837e+00,
                     4.58104245e+00, 4.57557976e+00, 4.57090657e+00, 4.56701796e+00,
                     4.56391110e+00, 4.56158463e+00, 4.56003705e+00, 4.55926897e+00,
                     4.55928067e+00, 4.56007812e+00, 4.56166478e+00, 4.56404380e+00,
                     4.56722299e+00, 4.57121182e+00, 4.57601689e+00, 4.58165014e+00,
                     4.58812667e+00, 4.59545495e+00, 4.60365391e+00, 4.61274222e+00,
                     4.62273305e+00, 4.63365501e+00, 4.64552513e+00, 4.65837310e+00,
                     4.67222773e+00, 4.68711666e+00, 4.70307602e+00, 4.72014236e+00,
                     4.73835953e+00, 4.75776969e+00, 4.77842149e+00, 4.80037180e+00,
                     4.82368131e+00, 4.84841647e+00, 4.87464820e+00, 4.90246330e+00,
                     4.93194861e+00, 4.96320960e+00, 4.99635810e+00, 5.03152302e+00,
                     5.06884667e+00, 5.10849298e+00, 5.15065255e+00, 5.19553034e+00,
                     5.24337309e+00, 5.29446289e+00, 5.34912336e+00, 5.40773586e+00,
                     5.47074971e+00, 5.53869610e+00, 5.61220226e+00, 5.69203799e+00,
                     5.77913228e+00, 5.87463232e+00, 5.97996396e+00, 6.09694062e+00,
                     6.22788833e+00, 6.37587244e+00, 6.54500327e+00, 6.74097217e+00,
                     6.97191064e+00, 7.25001021e+00, 7.59454361e+00, 8.03851538e+00,
                     8.64498429e+00, 9.55640128e+00, 1.12037571e+01, 1.61493962e+01,
                     1.74989866e-07, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 3.71422112e+01,
                     2.32797501e+01, 1.84007592e+01, 1.57144211e+01, 1.39570766e+01,
                     1.26947688e+01, 1.17325683e+01, 1.09686396e+01, 1.03436016e+01,
                     9.82040223e+00, 9.37441546e+00, 8.98868181e+00, 8.65098918e+00,
                     8.35236063e+00, 8.08600065e+00, 7.84664078e+00, 2.74573178e+01,
                     1.81116804e+01, 1.58872580e+01, 1.47687896e+01, 1.40620497e+01,
                     1.35602315e+01, 1.31775566e+01, 1.28712706e+01, 1.26174754e+01,
                     1.24015265e+01, 1.22139625e+01, 1.20483085e+01, 1.18999833e+01,
                     1.17656375e+01, 1.16427727e+01, 1.15294543e+01, 1.14241836e+01,
                     1.13257671e+01, 1.12332682e+01, 1.11458952e+01, 1.10630370e+01,
                     1.09841615e+01, 1.09088460e+01, 1.08367286e+01, 1.07675172e+01,
                     1.07009604e+01, 1.06368473e+01, 1.05750029e+01, 1.05152798e+01,
                     1.04575567e+01, 1.04017288e+01, 1.03477057e+01, 1.02954243e+01,
                     1.02448155e+01, 1.01958273e+01, 1.01484263e+01, 1.01025774e+01,
                     1.00582447e+01, 1.00154164e+01, 9.97406576e+00, 9.93418368e+00,
                     9.89575509e+00, 9.85877820e+00, 9.82324558e+00, 9.78914505e+00,
                     9.75648240e+00, 9.72525643e+00, 9.69546229e+00, 9.66710850e+00,
                     9.64019163e+00, 9.61471797e+00, 9.59068815e+00, 9.56810938e+00,
                     9.54698352e+00, 9.52732319e+00, 9.50912888e+00, 9.49240803e+00,
                     9.47717048e+00, 9.46342604e+00, 9.45118219e+00, 9.44044847e+00,
                     9.43123395e+00, 9.42355609e+00, 9.41742474e+00, 9.41285366e+00,
                     9.40986017e+00, 9.40845814e+00, 9.40866537e+00, 9.41050590e+00,
                     9.41399686e+00, 9.41916509e+00, 9.42603203e+00, 9.43462298e+00,
                     9.44497240e+00, 9.45710837e+00, 9.47106615e+00, 9.48688529e+00,
                     9.50460299e+00, 9.52426386e+00, 9.54591043e+00, 9.56960385e+00,
                     9.59539164e+00, 9.62334157e+00, 9.65350730e+00, 9.68597143e+00,
                     9.72080418e+00, 9.75809140e+00, 9.79792534e+00, 9.84041140e+00,
                     9.88564877e+00, 9.93376490e+00, 9.98488750e+00, 1.00391592e+01,
                     1.00967456e+01, 1.01578202e+01, 1.02225764e+01, 1.02912318e+01,
                     1.03640326e+01, 1.04412364e+01, 1.05231582e+01, 1.06101382e+01,
                     1.07025606e+01, 1.08008671e+01, 1.09055699e+01, 1.10172424e+01,
                     1.11365667e+01, 1.12643339e+01, 1.14014719e+01, 1.15490904e+01,
                     1.17085185e+01, 1.18813900e+01, 1.20696945e+01, 1.22759550e+01,
                     1.25033666e+01, 1.27561337e+01, 1.30398970e+01, 1.33624634e+01,
                     1.37351456e+01, 1.41751913e+01, 1.47108919e+01, 1.53934209e+01,
                     1.63300836e+01, 1.78072635e+01, 2.10637590e+01, 7.67229363e+00,
                     7.89239320e+00, 8.13599128e+00, 8.40816266e+00, 8.71466524e+00,
                     9.06294873e+00, 9.46301389e+00, 9.92852760e+00, 1.04788319e+01,
                     1.11423308e+01, 1.19628568e+01, 1.30123464e+01, 1.44192270e+01,
                     1.64422154e+01, 1.97111534e+01, 2.64042837e+01, 5.96936742e+01,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.20388170e+01,
                     9.12526890e+00, 7.93702799e+00, 7.28315965e+00, 6.87047854e+00,
                     6.58813046e+00, 6.38420797e+00, 6.23091858e+00, 6.11204287e+00,
                     6.01739949e+00, 5.94030866e+00, 5.87620517e+00, 5.82187008e+00,
                     5.77496823e+00, 5.73378355e+00, 5.69702456e+00, 5.66370589e+00,
                     5.63307652e+00, 5.60454931e+00, 5.57767072e+00, 5.55208157e+00,
                     5.52750304e+00, 5.50372163e+00, 5.48056393e+00, 5.45790316e+00,
                     5.43563835e+00, 5.41369581e+00, 5.39202476e+00, 5.37058565e+00,
                     5.34935870e+00, 5.32833039e+00, 5.30749722e+00, 5.28686356e+00,
                     5.26643796e+00, 5.24623572e+00, 5.22627441e+00, 5.20657254e+00,
                     5.18715388e+00, 5.16803938e+00, 5.14925635e+00, 5.13082626e+00,
                     5.11277730e+00, 5.09512993e+00, 5.07791381e+00, 5.06114762e+00,
                     5.04485702e+00, 5.02906543e+00, 5.01379366e+00, 4.99906234e+00,
                     4.98489324e+00, 4.97130488e+00, 4.95831425e+00, 4.94594083e+00,
                     4.93420314e+00, 4.92311505e+00, 4.91269298e+00, 4.90295309e+00,
                     4.89390732e+00, 4.88557339e+00, 4.87796081e+00, 4.87108785e+00,
                     4.86496230e+00, 4.85960066e+00, 4.85501678e+00, 4.85122010e+00,
                     4.84822578e+00, 4.84604605e+00, 4.84469472e+00, 4.84418656e+00,
                     4.84453071e+00, 4.84574957e+00, 4.84785100e+00, 4.85085108e+00,
                     4.85477314e+00, 4.85962568e+00, 4.86543069e+00, 4.87221120e+00,
                     4.87998473e+00, 4.88877291e+00, 4.89859605e+00, 4.90948652e+00,
                     4.92146323e+00, 4.93456062e+00, 4.94880448e+00, 4.96422767e+00,
                     4.98087282e+00, 4.99876729e+00, 5.01795964e+00, 5.03849161e+00,
                     5.06040826e+00, 5.08376012e+00, 5.10860510e+00, 5.13500374e+00,
                     5.16302043e+00, 5.19272007e+00, 5.22418529e+00, 5.25749158e+00,
                     5.29273489e+00, 5.33000857e+00, 5.36942449e+00, 5.41109207e+00,
                     5.45514593e+00, 5.50172363e+00, 5.55096928e+00, 5.60307356e+00,
                     5.65820739e+00, 5.71658090e+00, 5.77842769e+00, 5.84400282e+00,
                     5.91358588e+00, 5.98750610e+00, 6.06611612e+00, 6.14982463e+00,
                     6.23908972e+00, 6.33443324e+00, 6.43645856e+00, 6.54583690e+00,
                     6.66336836e+00, 6.78997813e+00, 6.92672776e+00, 7.07490485e+00,
                     7.23598544e+00, 7.41179256e+00, 7.60448761e+00, 7.81674913e+00,
                     8.05185813e+00, 8.31394887e+00, 8.60827163e+00, 8.94163156e+00,
                     9.32316947e+00, 9.76503152e+00, 1.02844665e+01, 1.09062991e+01,
                     1.16682403e+01, 1.26308007e+01, 1.38986357e+01, 1.56732744e+01,
                     1.84101268e+01, 2.34677863e+01, 3.87261424e+01, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                     0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00])


def expected_tr_of_complex_chain():
    return np.array([1.69332444e-10, -6.68995731e-11, 4.73484361e-10, 1.17698445e-10,
                     6.90455514e-11, 1.97689383e-10, 2.44794545e-10, 1.66317366e-10,
                     1.41054215e-10, -4.92820453e-11, 7.27091765e-11, -4.43352357e-10,
                     5.53157915e-11, -1.85762328e-10, 9.51262543e-10, -4.63452731e-10,
                     5.68308558e-10, 1.56573408e-10, -1.27783215e-10, 2.36901711e-10,
                     2.30163552e-10, 4.33243155e-10, 2.51405895e-10, 1.59814452e-10,
                     2.77349993e-10, 2.59491204e-10, -1.88265688e-10, 3.98908795e-10,
                     6.34611166e-10, -2.85458686e-10, 2.91584056e-10, 4.14478443e-11,
                     -5.45051538e-10, 8.14221619e-11, 1.42413634e-09, -6.95349223e-11,
                     5.32600347e-10, -5.22654380e-10, -9.87644688e-10, -4.00741209e-10,
                     3.06197706e-10, -1.07307811e-09, 5.29553343e-11, 1.33005891e-09,
                     -1.16992557e-10, 1.41085140e-09, -1.15505530e-09, -5.23936984e-10,
                     1.18787815e-09, 1.21649195e-10, 1.28562656e-09, 1.54505865e-10,
                     5.76389179e-10, 1.35124787e-09, -6.41079411e-10, 2.46240617e-10,
                     7.62235367e-10, 1.15776682e-09, 6.75381335e-10, -3.34753648e-10,
                     8.44311802e-11, 1.65282625e-09, -1.14796078e-09, -7.11932262e-10,
                     1.08934449e-09, 2.38669928e-09, 1.85143391e-09, 2.16620642e-09,
                     7.59169296e-10, -7.25107539e-10, -6.18773499e-11, -2.58548873e-10,
                     -7.61470691e-10, 1.90688249e-09, 1.59059875e-09, 2.50842038e-10,
                     3.80252237e-09, 9.17007459e-10, 3.25722035e-09, -4.19631438e-10,
                     9.14649541e-10, 8.63967690e-10, 2.41493221e-09, -3.48682006e-09,
                     2.35891626e-09, 2.39930275e-09, 1.42049914e-09, 1.31893904e-09,
                     3.91448929e-09, 3.40431978e-09, 7.25934184e-10, 2.43384360e-09,
                     2.05812685e-09, 4.50381729e-09, 8.37939282e-10, 4.01534663e-09,
                     -1.27908503e-09, 2.19079026e-09, 2.99308648e-09, 6.89709232e-09,
                     1.03935390e-08, 1.24043492e-08, 3.35955606e-09, 7.23902703e-09,
                     4.97426958e-09, -8.52174011e-09, 5.70258735e-10, 1.22077540e-08,
                     4.70868252e-09, 2.49934548e-09, 6.60842840e-11, -1.14540448e-08,
                     2.18033834e-09, 1.55070464e-08, 1.13069006e-08, 9.74032274e-09,
                     2.48189765e-08, 8.52006517e-09, -8.41007706e-09, -1.45978581e-08,
                     5.87004909e-10, 3.03794378e-08, -7.02909252e-09, 1.79256691e-08,
                     1.11394260e-08, -7.56854630e-09, -4.47091155e-09, 2.70363743e-08,
                     2.53295436e-08, 4.39461959e-08, 1.84469882e-08, 3.90161357e-08,
                     9.79279855e-08, 1.63731912e-07, 6.36608499e-08, 9.64824674e-08,
                     -1.22779903e-07, 9.28831479e-08, 3.23020619e-07, 4.94206226e-06,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     9.99999999e-01, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     1.00000000e+00, 9.99999999e-01, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 9.99999999e-01, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 9.99999999e-01,
                     9.99999998e-01, 9.99999999e-01, 1.00000000e+00, 9.99999999e-01,
                     9.99999999e-01, 9.99999999e-01, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     9.99999999e-01, 1.00000000e+00, 1.00000000e+00, 9.99999999e-01,
                     1.00000000e+00, 1.00000001e+00, 1.00000000e+00, 9.99999998e-01,
                     9.99999999e-01, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     9.99999996e-01, 1.00000000e+00, 1.00000001e+00, 1.00000000e+00,
                     9.99999997e-01, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000001e+00, 9.99999996e-01, 1.00000001e+00, 1.00000001e+00,
                     9.99999999e-01, 9.99999995e-01, 1.00000000e+00, 1.00000001e+00,
                     1.00000000e+00, 9.99999997e-01, 1.00000001e+00, 1.00000000e+00,
                     9.99999993e-01, 1.00000001e+00, 9.99999985e-01, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000001e+00, 1.00000001e+00,
                     1.00000001e+00, 1.00000002e+00, 1.00000000e+00, 9.99999976e-01,
                     9.99999985e-01, 9.99999986e-01, 1.00000003e+00, 1.00000000e+00,
                     3.73533591e-08, 5.41874473e-08, 1.28835425e-07, -2.05098112e-08,
                     -5.24588173e-08, 2.53455965e-08, 4.41906757e-09, 1.61776862e-07,
                     -5.26701247e-08, -9.68757597e-08, -2.63520696e-08, 1.54364805e-07,
                     -1.22587314e-07, 4.27840068e-08, 6.96128963e-07, 9.99999983e-01,
                     9.99999988e-01, 1.00000003e+00, 1.00000004e+00, 1.00000000e+00,
                     1.00000001e+00, 9.99999992e-01, 9.99999953e-01, 9.99999977e-01,
                     9.99999968e-01, 1.00000000e+00, 1.00000002e+00, 9.99999977e-01,
                     1.00000001e+00, 9.99999987e-01, 1.00000001e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 2.00000000e+00,
                     2.00000000e+00, 2.00000000e+00, 2.00000000e+00, 1.00000005e+00,
                     1.00000019e+00, 9.99999932e-01, 1.00000001e+00, 9.99999941e-01,
                     9.99999889e-01, 1.00000000e+00, 1.00000004e+00, 9.99999819e-01,
                     9.99999905e-01, 9.99999921e-01, 9.99999964e-01, 1.00000004e+00,
                     9.99999930e-01, 9.99999992e-01, 9.99999927e-01, 9.99999955e-01,
                     7.17837277e-07, -6.45034977e-08, 4.04207407e-08, 2.20909180e-08,
                     7.68606053e-08, -1.65388551e-08, 1.20178607e-07, 1.22471770e-08,
                     -1.43052140e-08, -5.22024028e-08, 1.90686847e-08, -1.84112150e-08,
                     -5.42782226e-09, 1.42945757e-08, -1.25137129e-08, 1.00000002e+00,
                     1.00000001e+00, 1.00000000e+00, 1.00000003e+00, 1.00000002e+00,
                     9.99999993e-01, 1.00000001e+00, 1.00000002e+00, 1.00000001e+00,
                     1.00000001e+00, 9.99999990e-01, 1.00000001e+00, 1.00000001e+00,
                     9.99999998e-01, 9.99999984e-01, 1.00000001e+00, 1.00000001e+00,
                     1.00000001e+00, 9.99999991e-01, 9.99999997e-01, 1.00000000e+00,
                     1.00000000e+00, 1.00000001e+00, 1.00000000e+00, 1.00000001e+00,
                     1.00000000e+00, 1.00000001e+00, 1.00000001e+00, 9.99999996e-01,
                     1.00000001e+00, 1.00000000e+00, 9.99999999e-01, 9.99999999e-01,
                     9.99999997e-01, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 9.99999998e-01, 1.00000000e+00, 9.99999999e-01,
                     9.99999996e-01, 1.00000000e+00, 9.99999998e-01, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 9.99999998e-01,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     9.99999999e-01, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     1.00000000e+00, 9.99999999e-01, 9.99999999e-01, 1.00000000e+00,
                     9.99999999e-01, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     9.99999999e-01, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 9.99999999e-01, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 1.00000000e+00,
                     1.00000000e+00, 1.00000000e+00, 1.00000000e+00, 4.61091214e-07,
                     1.49465450e-07, 1.33502144e-07, -4.67741630e-08, 1.29395749e-07,
                     -1.17935355e-07, 5.45763144e-08, 6.34153919e-08, 8.04431262e-09,
                     2.09005334e-08, -3.45311140e-08, -1.15070047e-08, -3.52597501e-08,
                     8.72949835e-08, -2.15103671e-08, -2.40377224e-09, 2.59433195e-08,
                     2.89077408e-08, 3.86750160e-08, 2.47704705e-08, 1.08087715e-08,
                     6.73645456e-09, 1.39984742e-08, 1.19509101e-08, 9.61479127e-09,
                     1.38007395e-08, 4.31373179e-09, 1.35299508e-08, 1.53621194e-08,
                     -4.06734126e-09, 1.71738578e-08, 9.35480679e-09, -7.98127541e-09,
                     1.41066232e-08, -5.08720225e-09, -8.08506896e-10, 9.19824862e-09,
                     6.05163653e-09, 2.57949760e-09, 6.17249518e-09, -3.07332128e-09,
                     -5.17534660e-09, 3.76601890e-09, 2.79637610e-09, 7.20656571e-09,
                     2.13265370e-10, -7.98108815e-10, 1.26378881e-09, 6.95694303e-09,
                     2.76271205e-09, 7.32674139e-09, -5.72364014e-10, 2.71722136e-09,
                     2.02700930e-09, 1.55890384e-09, 3.30323736e-09, -1.67386915e-10,
                     -1.29972751e-09, 8.08482179e-10, -7.53464296e-12, 5.63087910e-10,
                     2.29918377e-09, -1.31539600e-10, 1.01932446e-09, 2.93720403e-09,
                     8.33685469e-10, -5.68029870e-10, -1.43635084e-09, -1.34173789e-09,
                     -7.94809497e-10, 2.06089927e-09, 6.64943225e-10, 2.65125517e-09,
                     1.95859351e-09, 1.93145662e-09, -1.74710126e-10, 2.48390580e-09,
                     6.35467022e-10, -9.85154233e-10, -5.77657637e-10, 6.75535315e-10,
                     1.27529176e-09, -4.01940117e-10, 8.64875296e-11, -7.58459961e-10,
                     6.25752240e-10, -1.61717618e-09, -4.04421204e-10, 3.56904960e-10,
                     3.64201443e-10, -1.02242500e-09, 4.11720643e-10, -3.92885224e-10])


def inverse_bs_problem():
    import sys
    sys.path.insert(0, '/home/mk/TB_project/tb')
    import tb

    # a = tb.Atom('A')
    # a.add_orbital('s', -0.7)
    # b = tb.Atom('B')
    # b.add_orbital('s', -0.5)
    # c = tb.Atom('C')
    # c.add_orbital('s', -0.3)
    #
    # tb.Atom.orbital_sets = {'A': a, 'B': b, 'C': c}
    #
    # tb.set_tb_params(PARAMS_A_A={'ss_sigma': -0.5},
    #                  PARAMS_B_B={'ss_sigma': -0.5},
    #                  PARAMS_C_C={'ss_sigma': -0.5},
    #                  PARAMS_A_B={'ss_sigma': -0.5},
    #                  PARAMS_B_C={'ss_sigma': -0.5},
    #                  PARAMS_A_C={'ss_sigma': -0.5})
    #
    # xyz_file = """6
    # H cell
    # A1       0.0000000000    0.0000000000    0.0000000000
    # B2       0.0000000000    0.0000000000    1.0000000000
    # C3       0.0000000000    0.0000000000    2.0000000000
    # A4       0.0000000000    1.0000000000    0.0000000000
    # B5       0.0000000000    1.0000000000    1.0000000000
    # C6       0.0000000000    1.0000000000    2.0000000000
    # """
    #
    # h = tb.Hamiltonian(xyz=xyz_file, nn_distance=1.1)
    # h.initialize()
    # h.set_periodic_bc([[0, 0, 3.0]])

    tb.Atom.orbital_sets = {'Si': 'SiliconSP3D5S', 'H': 'HydrogenS'}
    h = tb.Hamiltonian(xyz='/home/mk/TB_project/input_samples/SiNW.xyz', nn_distance=2.4)
    h.initialize()
    h.set_periodic_bc([[0, 0, 5.50]])

    h_l, h_0, h_r = h.get_coupling_hamiltonians()

    energy = np.linspace(2.13, 2.15, 20)
    # energy = np.linspace(-2.1, 1.0, 50)
    energy = np.linspace(2.05, 2.5, 100)[70:85]

    energy = np.linspace(2.07, 2.3, 50) + 0.2
    # energy = np.linspace(2.3950, 2.4050, 20)

    energy = energy[20:]

    eigs = []

    for E in energy:

        print E

        vals, vects = tb.surface_greens_function_poles(E, h_l, h_0, h_r)

        vals = np.diag(vals)
        vals.setflags(write=1)

        for j, v in enumerate(vals):

            if np.abs(np.absolute(v) - 1.0) > 0.01:
                vals[j] = float('nan')
            else:
                vals[j] = np.angle(v)
                print "The element number is", j, vals[j]

        eigs.append(vals)

    plt.plot(energy, np.array(eigs), 'o')
    plt.show()


def main2():
    import sys
    sys.path.insert(0, '/home/mk/TB_project/tb')
    import tb

    a = tb.Atom('A')
    a.add_orbital('s', -0.7)

    tb.Atom.orbital_sets = {'A': a}

    tb.set_tb_params(PARAMS_A_A={'ss_sigma': -0.5},
                     PARAMS_B_B={'ss_sigma': -0.5},
                     PARAMS_A_B={'ss_sigma': -0.5},
                     PARAMS_B_C={'ss_sigma': -0.5},
                     PARAMS_A_C={'ss_sigma': -0.5})

    xyz_file = """1
    H cell
    A1       0.0000000000    0.0000000000    0.0000000000                                                                                                      
    """

    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=2.1)
    h.initialize()
    h.set_periodic_bc([[0, 0, 1.0]])
    h_l, h_0, h_r = h.get_coupling_hamiltonians()

    energy = np.linspace(-3.0, 1.5, 700)

    sgf_l = []
    sgf_r = []

    for E in energy:
        L, R, _, _, _ = tb.surface_greens_function(E, h_l, h_0, h_r)
        # L, R = surface_greens_function_poles_Shur(E, h_l, h_0, h_r)
        sgf_l.append(L)
        sgf_r.append(R)

    sgf_l = np.array(sgf_l)
    sgf_r = np.array(sgf_r)

    num_sites = h_0.shape[0]
    gf = np.linalg.pinv(np.multiply.outer(energy, np.identity(num_sites)) - h_0 - sgf_l - sgf_r)

    dos = -np.trace(np.imag(gf), axis1=1, axis2=2)

    tr = np.zeros((energy.shape[0]), dtype=np.complex)

    for j, E in enumerate(energy):
        gf0 = np.matrix(gf[j, :, :])
        gamma_l = 1j * (np.matrix(sgf_l[j, :, :]) - np.matrix(sgf_l[j, :, :]).H)
        gamma_r = 1j * (np.matrix(sgf_r[j, :, :]) - np.matrix(sgf_r[j, :, :]).H)
        tr[j] = np.real(np.trace(gamma_l * gf0 * gamma_r * gf0.H))
        dos[j] = np.real(np.trace(1j * (gf0 - gf0.H)))
    print sgf_l.shape


def main3():
    import sys
    sys.path.insert(0, '/home/mk/TB_project/tb')
    import tb

    a = tb.Atom('A')
    a.add_orbital('s', -0.7)

    tb.Atom.orbital_sets = {'A': a}

    tb.set_tb_params(PARAMS_A_A={'ss_sigma': -0.5},
                     PARAMS_B_B={'ss_sigma': -0.5},
                     PARAMS_A_B={'ss_sigma': -0.5},
                     PARAMS_B_C={'ss_sigma': -0.5},
                     PARAMS_A_C={'ss_sigma': -0.5})

    xyz_file = """1
    H cell
    A1       0.0000000000    0.0000000000    0.0000000000                                                                                                      
    """

    h = tb.Hamiltonian(xyz=xyz_file, nn_distance=2.1)
    h.initialize()
    h.set_periodic_bc([[0, 0, 1.0]])
    h_l, h_0, h_r = h.get_coupling_hamiltonians()

    energy = np.linspace(-3.0, 1.5, 700)

    sgf_l = []
    sgf_r = []

    for E in energy:
        L, R, _, _, _ = tb.surface_greens_function(E, h_l, h_0, h_r)
        # L, R = surface_greens_function_poles_Shur(E, h_l, h_0, h_r)
        sgf_l.append(L)
        sgf_r.append(R)

    sgf_l = np.array(sgf_l)
    sgf_r = np.array(sgf_r)

    num_sites = h_0.shape[0]
    gf = np.linalg.pinv(np.multiply.outer(energy, np.identity(num_sites)) - h_0 - sgf_l - sgf_r)

    dos = -np.trace(np.imag(gf), axis1=1, axis2=2)

    tr = np.zeros((energy.shape[0]), dtype=np.complex)

    for j, E in enumerate(energy):
        gf0 = np.matrix(gf[j, :, :])
        gamma_l = 1j * (np.matrix(sgf_l[j, :, :]) - np.matrix(sgf_l[j, :, :]).H)
        gamma_r = 1j * (np.matrix(sgf_r[j, :, :]) - np.matrix(sgf_r[j, :, :]).H)
        tr[j] = np.real(np.trace(gamma_l * gf0 * gamma_r * gf0.H))
        dos[j] = np.real(np.trace(1j * (gf0 - gf0.H)))
    print sgf_l.shape


if __name__ == "__main__":
    test_gf_single_atom_chain()
    test_gf_complex_chain()