import { Component, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {BasicTemplateService} from "../../services/basicTemplate.service";

@Component({
  selector: 'app-basicTemplate',
  templateUrl: './basicTemplate.component.html',
  styleUrls: ['./basicTemplate.component.less']
})
export class BasicTemplateComponent implements OnInit {

   message: string = '';
  constructor(
    private httpClient: HttpClient,
    private basicTemplateService: BasicTemplateService
  ) {
    this.basicTemplateService.hello_word().then(value => {
      this.message = value
    })
  }

  ngOnInit(): void {
  }

}
