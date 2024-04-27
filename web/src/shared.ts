

export const HOST="http://localhost:5000/"

export interface Page {
  number: number,
  title: string,
  text: string,
  type: "query" | "display",
  img_url: string,
}

export interface Story {
  _id: string,
  name: string,
  company: string,
  tagline: string,
  pages: Page[],
}
