#include "TTree.h"
#include "TFile.h"
#include "TF1.h"
#include "TH1.h"
#include "TCanvas.h"

// Ped part:always using L method since it is much better than chi2 method

void fitHistograms(TString filename, TString dirname)
{
  TFile *file = new TFile(filename);
  TIter next(file->GetListOfKeys());
  TKey *key;
  while ((key = (TKey*)next()))
  {
    TObject *obj = key->ReadObj();
    if (obj->IsA()->InheritsFrom("TH2"))
    {
      TH2F *h2 = (TH2F*)obj;
      TString hname = h2->GetName();
      TCanvas *c = new TCanvas();

      for (int binx = 1; binx <= h2->GetNbinsX(); binx++)
      {
        TString slice_hist_name = Form("%s_slice_%d", hname.Data(), binx);
        TH1D *h1 = h2->ProjectionY(slice_hist_name, binx, binx);
        
        // Increase the range of the fit
        TF1 *fitfunc = new TF1("fitfunc", "landau", h1->GetXaxis()->GetXmin(), h1->GetXaxis()->GetXmax());
        h1->Fit(fitfunc, "Q");

        c->Clear();
        h1->SetStats(kFALSE);
        h1->SetTitle("Your Histogram Title");
        h1->Draw();
        fitfunc->Draw("SAME");
        TString pdf_filename = Form("%s.pdf", slice_hist_name.Data());
        c->SaveAs(dirname + "/" + pdf_filename);
      }
    }
  }
}
