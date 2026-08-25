interface Props {
  type: "loading" | "error" | "empty";
  message: string;
}

export function StatusMessage({ type, message }: Props) {
  const styles = {
    loading: "text-blue-600 bg-blue-50",
    error: "text-red-600 bg-red-50",
    empty: "text-gray-600 bg-gray-50",
  };

  return (
    <div className={`p-4 rounded-lg text-center ${styles[type]}`}>
      {message}
    </div>
  );
}
