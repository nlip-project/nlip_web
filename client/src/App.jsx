import Text from "./components/Text"
import Products from "./components/Products"
import Image from "./components/Image"

function App() {
  const mode = import.meta.env.VITE_APP_MODE || 'image';

  if (mode === "text") return <Text />
  if (mode === "products") return <Products />
  if (mode === "image") return <Image />

  return (
    <>
      <Text />
      <Products />
      <Image />
    </>
  )
}

export default App
