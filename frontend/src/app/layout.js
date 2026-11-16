import "./globals.css";
export const metadata = {
  title: "HostelSpace",
  description: "Student and hostel staff portal",
};
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
