/**
 * Defines the info of the server's machine.
 */
export class MachineInfo {

  constructor(machineInfoResponse: any) {
    this.name = machineInfoResponse.name;
    this.hostname = machineInfoResponse.hostname;
  }

  /**
   * The name of the machine.
   */
  name: string;

  /**
   * The hostname of the machine.
   */
  hostname: string;

}
