import { Config } from "./src/config";

export const defaultConfig: Config = {
  url: "https://grad.tamu.edu/about-the-graduate-and-professional-school/admissions",
  match: "https://gsas.harvard.edu/apply/**",
  maxPagesToCrawl: 200,
  outputFileName: "output1\.json",
  maxTokens: 2000000,
};
