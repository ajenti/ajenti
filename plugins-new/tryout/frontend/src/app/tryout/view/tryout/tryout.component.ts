import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {TryoutService} from "../../services/tryout.service";

@Component({
  selector: 'app-tryout',
  templateUrl: './tryout.component.html',
  styleUrls: ['./tryout.component.css']
})
export class TryoutComponent implements OnInit {
  message: string = '';
  constructor(
    private httpClient: HttpClient,
    private tryoutService: TryoutService
  ) {
    this.tryoutService.hello_word().then(value => {
      this.message = value
    })
  }

  ngOnInit(): void {
  }

}
