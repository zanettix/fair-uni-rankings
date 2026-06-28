import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UltimateRanking } from '../../models/ranking.model';


@Component({
  selector: 'app-ranking-table',
  templateUrl: './ranking-table-component.html',
  styleUrls: ['./ranking-table-component.css']
})
export class RankingTableComponent implements OnInit {
  rankings: UltimateRanking[] = [];

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Angular serve automaticamente la cartella assets/
    this.http.get<UltimateRanking[]>('/assets/rankings/ultimate-ranking.json')
      .subscribe({
        next: (data) => {
          // Ci assicuriamo che siano ordinati per il rank finale
          this.rankings = data.sort((a, b) => a.ultimate_rank - b.ultimate_rank);
        },
        error: (err) => {
          console.error('Errore nel caricamento del JSON:', err);
        }
      });
  }
}