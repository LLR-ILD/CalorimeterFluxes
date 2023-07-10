import ROOT

# Open the root file
file = ROOT.TFile("data/v5_small/mu-/2D_histograms/all.root")

# Get the list of keys
keys = file.GetListOfKeys()

# Print the name and class of each object
for key in keys:
    print("Name: {}, Class: {}".format(key.GetName(), key.GetClassName()))
