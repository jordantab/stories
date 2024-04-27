

export const HOST="http://127.0.0.1:5000/"

export interface Page {
  number: number,
  title: string,
  text: string,
  type: "query" | "display",
  img_url: string,
  query_key?: string,
}

export interface Story {
  _id: string,
  name: string,
  company: string,
  tagline: string,
  pages: Page[],
}
