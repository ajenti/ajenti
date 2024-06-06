export class AjentiUser {

  constructor(ajentiUserResponse: AjentiUser) {
    this.password = ajentiUserResponse.password;
    this.uid = ajentiUserResponse.uid;
  }

  public password: string;
  public uid: number;

}
