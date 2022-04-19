import { Component, OnInit } from '@angular/core';
import { Task, TaskService } from '@ngx-ajenti/core';

@Component({
  selector: 'app-side-bar-tasks',
  templateUrl: './side-bar-tasks.component.html',
  styleUrls: [ './side-bar-tasks.component.less' ],
})
export class SideBarTasksComponent implements OnInit {

  public tasks: Task[];

  constructor(private tasksService: TaskService) {
    this.tasks = [];
  }

  ngOnInit(): void {
    this.tasksService.tasks.subscribe(tasks => {
      this.tasks = tasks;
    });
  }

}
