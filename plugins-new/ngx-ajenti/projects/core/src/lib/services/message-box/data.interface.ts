export interface DataInterface<T = any> {

  setData(data: T): void;

  getData(): T;
}
