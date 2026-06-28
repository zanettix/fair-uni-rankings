export interface UltimateRanking {
  name: string;
  country: string;
  average_rank: number;
  sources_count: number;
  breakdown: {
    qs?: number;
    the?: number;
    arwu?: number;
    usnews?: number;
  };
  ultimate_rank: number;
}