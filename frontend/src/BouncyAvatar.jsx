import { motion } from "framer-motion";

export const BouncyAvatar = ({ src }) => (
  <motion.img
    src={src}
    alt="avatar"
    className="w-20 h-20 rounded-full"
    initial={{ scale: 0 }}
    animate={{ scale: 1 }}
    transition={{ type: "spring", stiffness: 300, damping: 15 }}
  />
);