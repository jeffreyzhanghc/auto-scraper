import { Config } from "./src/config";

export const defaultConfig: Config = {
  url: "https://gradadmissions.stanford.edu/",
  match: "https://gradadmissions.stanford.edu/**",
  maxPagesToCrawl: 200,
  outputFileName: "output1\.json",
  maxTokens: 2000000,
};
