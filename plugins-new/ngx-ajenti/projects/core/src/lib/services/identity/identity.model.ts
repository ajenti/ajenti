/**
 * Defines the identity of the user.
 */
export class Identity {

  constructor(identityApiResponse: any) {
    this.user = identityApiResponse.user || '';
    this.uid = identityApiResponse.uid || '';
    this.effectiveUid = identityApiResponse.effectiveUid || '';
    this.elevationAllowed = identityApiResponse.elevationAllowed || '';
    this.profile = identityApiResponse.profile || '';
  }

  /**
   * The name of the user.
   */
  public user: string;

  /**
   * The uid of the user.
   */
  public uid: number;

  /**
   * The effective uid of the user.
   */
  public effectiveUid: number;

  /**
   * Determines if the elevation is allowed or not.
   */
  public elevationAllowed: boolean;

  /**
   * The profile of the user.
   *
   * TODO: Define the correct type!
   */
  public profile?: {};

  /**
   * Determines if the user is a superuser.
   */
  public get isSuperuser() {
    const isSignedInAsSudo = this.user === 'root';
    const isSignedInAsRoot = this.effectiveUid === 0;
    return isSignedInAsSudo || isSignedInAsRoot;
  }

  /**
   * Determines if the user is logged in.
   */
  public get isUserSignedIn(): boolean {
    return !!this.user;
  }

}
